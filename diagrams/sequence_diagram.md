# VistaAI — Sequence Diagram

## As-Drawn (from handwritten sketch)

```mermaid
sequenceDiagram
    actor PO as Property Owner
    participant UI as Interface
    participant API as FastAPI Server
    participant IMG as Image Generate<br/>Pipeline
    participant VID as Video Generate<br/>Pipeline
    participant AUD as Audio Generate<br/>Pipeline

    PO->>UI: Upload Image
    PO->>UI: Upload Narration, Tone
    PO->>UI: Click Generate Video

    UI->>API: POST /generate-room-tour

    API->>IMG: Forward Validated Image
    IMG-->>API: Return Transformed Image

    API->>VID: Forward Validated Image<br/>& Transformed Image
    VID-->>API: Return Video

    API->>AUD: Forward Generated Video<br/>& Merged Narration
    AUD-->>API: Script, Audio Script<br/>(Text & Audio)

    API-->>UI: Return Contents
    UI-->>PO: Stitched Generated Videos<br/>+ Narration Audio
```

---

## Corrected Version (aligned to actual codebase)

> [!NOTE]
> Corrections based on actual code flow in `logics/main.py`:
> - **Image Pipeline** doesn't just transform — it first **analyzes** (room type detection) then **stages** (furniture generation). These are two separate AI calls.
> - **Audio Pipeline receives room context**, not "generated video & merged narration". The script is generated from room type + preference, not from the video.
> - **Post-Processing** is a separate step — FFmpeg handles text overlay, audio merge, and cross-fade stitching. This was missing from the original diagram.
> - **Video Pipeline** doesn't interact with Audio. FastAPI orchestrates them independently and merges results via VideoPostProcessor.
> - Added **error handling** alt block since the pipeline has try/catch at every stage.

```mermaid
sequenceDiagram
    actor PO as 🏠 Property Owner
    participant UI as Interface
    participant API as FastAPI Server
    participant IMG as ImageProcessor<br/>(Gemini Flash + Imagen)
    participant VID as VideoGenerator<br/>(Veo 3.1)
    participant SCR as ScriptGenerator<br/>(Gemini Flash + TTS)
    participant PP as VideoPostProcessor<br/>(FFmpeg)

    PO->>UI: Upload image_paths, preference, rough_notes
    UI->>API: POST /generate-full-property-tour

    Note over API: Phase 1 — Image Analysis & Staging

    loop For each room image
        API->>IMG: transform_image(image_path)
        activate IMG
        IMG->>IMG: prompt_generate() → room_type, staging_prompt
        IMG->>IMG: Generate staged image via Imagen
        IMG-->>API: {room_type, staged_image_path}
        deactivate IMG
    end

    Note over API: Phase 2 — Video Generation

    loop For each room
        API->>VID: generate_transition(original, staged)
        activate VID
        VID->>VID: Poll until Veo completes
        VID-->>API: raw_video.mp4
        deactivate VID
    end

    Note over API: Phase 3 — Narration

    API->>SCR: generate_master_script(room_sequence, notes, preference)
    activate SCR
    SCR-->>API: {tour_script: [{narration_text, ...}]}
    deactivate SCR

    loop For each room
        API->>SCR: generate_audio(narration_text, voice)
        activate SCR
        SCR->>SCR: TTS → PCM → pad/trim to 4s
        SCR-->>API: audio_file.wav
        deactivate SCR
    end

    Note over API: Phase 4 — Assembly

    loop For each room clip
        API->>PP: add_text_overlay(raw_video, room_type)
        activate PP
        PP-->>API: overlaid_video.mp4 (muted)
        deactivate PP

        API->>PP: combine_video_audio(overlaid_video, audio)
        activate PP
        PP-->>API: final_clip.mp4
        deactivate PP
    end

    Note over API: Phase 5 — Stitching

    API->>PP: concatenate_with_transitions(all_clips)
    activate PP
    PP->>PP: FFmpeg xfade + acrossfade
    PP-->>API: master_tour.mp4
    deactivate PP

    API-->>UI: {status: success, full_tour_path, clips[]}
    UI-->>PO: Display final property tour video

    alt Pipeline Error
        API-->>UI: {status: 500, detail: error}
        UI-->>PO: Show error message
    end
```

---

## Corrections Summary

| Handwritten | Corrected | Reason |
|---|---|---|
| "Forward Validated Image" → Image Pipeline | `transform_image()` which internally calls `prompt_generate()` first | Two-step process: analyze room type → then generate staged image |
| Audio receives "Generated Video & Merged Narration" | Script generated from **room_type + preference**, NOT from video | `generate_master_script()` takes room sequence, not video data |
| *(missing)* | **Phase 4: Post-Processing** with FFmpeg | Text overlay (muted) + audio merge is a distinct step via `VideoPostProcessor` |
| *(missing)* | **Phase 5: Stitching** with xfade transitions | `concatenate_with_transitions()` is the final assembly step |
| Single pass flow | **Loop blocks** for multi-room processing | The full tour endpoint processes N rooms sequentially |
| *(missing)* | **Error handling** alt block | Pipeline wraps everything in try/catch, returns 500 on failure |
| 5 participants | **6 participants** — added PostProcessor | FFmpeg post-processing is a separate class (`VideoPostProcessor`) |

---

## Compact Version (PPT-Ready)

```mermaid
sequenceDiagram
    actor User as Property Owner
    participant API as FastAPI
    participant IMG as ImageProcessor
    participant VID as VideoGenerator
    participant SCR as ScriptGenerator
    participant FFM as FFmpeg Studio

    User->>API: images + preference + notes

    rect rgb(219, 234, 254)
    Note right of API: 1 — Staging
    API->>IMG: Analyze & stage rooms
    IMG-->>API: room_type + staged_image
    end

    rect rgb(220, 252, 231)
    Note right of API: 2 — Video
    API->>VID: Generate transitions
    VID-->>API: raw_video.mp4
    end

    rect rgb(254, 249, 195)
    Note right of API: 3 — Narration
    API->>SCR: Generate script + TTS audio
    SCR-->>API: narration.wav
    end

    rect rgb(252, 231, 243)
    Note right of API: 4 — Assembly & Stitch
    API->>FFM: Overlay + merge + xfade
    FFM-->>API: final_tour.mp4
    end

    API-->>User: Final property tour video
```
