# VistaAI — Activity Diagram

## As-Drawn (from handwritten sketch)

```mermaid
flowchart TD
    S(( )) --> A([User Upload Property Images])
    A --> B([Validate Images])
    B --> C([Upload & Update Narration, Tone])
    C --> D([Transformed Images])
    D --> E([Generate Videos])
    E --> F([Script Generation])
    F --> G([Audio Generate])
    G --> H([Stitch Content])
    H --> I([Return Generated Video])
    I --> Z((◉))
```

---

## Corrected Version (aligned to actual codebase)

> [!NOTE]
> Corrections:
> - **Narration/Tone is not uploaded separately** — it's part of the initial request as `preference` and `rough_notes`
> - **"Transformed Images"** is an action, not a state — renamed to **"Analyze & Stage Rooms"**
> - Added **decision nodes** — image validation can fail, video generation can fail
> - **Script and Audio are sequential**, not parallel — script must exist before TTS runs
> - **Assembly has 3 sub-steps** — text overlay, audio merge, then xfade stitch (not just "stitch")
> - Added **parallel fork** — Video generation and Script generation can logically run in parallel per room

```mermaid
flowchart TD
    S(( )) --> A

    A([User Submits Images\n+ Preference + Notes])
    A --> B{Images Exist?}

    B -->|No| ERR1([Return 404 Error])
    ERR1 --> Z

    B -->|Yes| C([Analyze Room Type\nvia Gemini Vision])
    C --> D([Generate Staged Image\nvia Imagen])

    D --> E{More Rooms?}
    E -->|Yes| C
    E -->|No| F

    F([Generate Transition Videos\nvia Veo 3.1]) --> G{Video Ready?}

    G -->|Polling...| F
    G -->|Done| H

    H([Generate Master\nNarration Script]) --> I([Generate TTS Audio\npad/trim to 4s])

    I --> J([Add Text Overlay\n+ Mute Source Audio])
    J --> K([Merge Video + Audio\nper Room Clip])

    K --> L{More Clips?}
    L -->|Yes| J
    L -->|No| M

    M([Stitch All Clips\nwith Crossfade Transitions])
    M --> N([Return Final\nProperty Tour Video])

    N --> Z((◉))

    style S fill:#000,stroke:#000,color:#fff
    style Z fill:#000,stroke:#333,color:#fff
    style ERR1 fill:#fca5a5,stroke:#dc2626
    style A fill:#c7d2fe,stroke:#4f46e5
    style C fill:#bfdbfe,stroke:#2563eb
    style D fill:#bfdbfe,stroke:#2563eb
    style F fill:#bbf7d0,stroke:#16a34a
    style H fill:#fef08a,stroke:#ca8a04
    style I fill:#fef08a,stroke:#ca8a04
    style J fill:#fbcfe8,stroke:#db2777
    style K fill:#fbcfe8,stroke:#db2777
    style M fill:#fbcfe8,stroke:#db2777
    style N fill:#d9f99d,stroke:#65a30d
```

---

## Compact Version (PPT-Ready)

```mermaid
flowchart TD
    S(( )) --> A([Upload Images + Preferences])
    A --> B{Valid?}
    B -->|No| X([Error])
    B -->|Yes| C([Analyze & Stage Rooms])
    C --> D([Generate Transition Videos])
    D --> E([Generate Script + Audio])
    E --> F([Overlay + Merge + Stitch])
    F --> G([Return Final Tour Video])
    G --> Z((◉))
    X --> Z

    style S fill:#000,stroke:#000,color:#fff
    style Z fill:#000,stroke:#333,color:#fff
    style X fill:#fca5a5,stroke:#dc2626
    style C fill:#bfdbfe,stroke:#2563eb
    style D fill:#bbf7d0,stroke:#16a34a
    style E fill:#fef08a,stroke:#ca8a04
    style F fill:#fbcfe8,stroke:#db2777
    style G fill:#d9f99d,stroke:#65a30d
```

---

## Corrections Summary

| Handwritten | Corrected | Reason |
|---|---|---|
| "Upload & Update Narration, Tone" as separate step | Merged into initial request | `preference` and `rough_notes` are fields on `TourRequest`, not a separate upload |
| "Transformed Images" (sounds like a state) | **Analyze Room Type** → **Generate Staged Image** (two actions) | `prompt_generate()` and `transform_image()` are two distinct AI calls |
| Purely linear flow | Added **decision nodes** for validation and loops | `os.path.exists()` check + loop over multiple rooms |
| "Stitch Content" (single step) | **3 sub-steps**: overlay → merge audio → xfade stitch | Maps to `add_text_overlay()`, `combine_video_audio()`, `concatenate_with_transitions()` |
| *(missing)* | **Error path** | Pipeline has try/catch returning HTTP 500 |
| *(missing)* | **Color coding** per pipeline phase | Blue=staging, Green=video, Yellow=narration, Pink=assembly |
