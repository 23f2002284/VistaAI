# VistaAI — Use Case Diagram

## As-Drawn (from handwritten sketch)

```mermaid
flowchart LR
    subgraph Actors
        PO(("🏠 Property\nOwner"))
        DA(("🔧 Developer\n/ Admin"))
    end

    subgraph VistaAI System
        UC1([Upload Image])
        UC2([Update Narration & Tone])
        UC3([Review Generated Video])
        UC4([Regenerate Video with\nUpdated Requirements])
        UC5([User Management\n& Access Control])
        UC6([Video Generation\n& Update Log])
    end

    PO --- UC1
    PO --- UC2
    PO --- UC3
    PO --- UC4

    UC2 -.->|"«extends»"| UC3

    DA --- UC5
    DA --- UC6
```

---

## Corrected Version (aligned to actual codebase)

> [!NOTE]
> Corrections & additions based on the actual VistaAI pipeline:
> - **Upload Image** → split into single room upload and multi-room batch upload (both endpoints exist)
> - **Added "Set Style Preference"** — the `preference` field is a core input in every request
> - **Added "Provide Rough Notes"** — the `rough_notes` field exists for the full tour endpoint
> - **"Review Generated Video"** now `<<includes>>` "Download Final Tour" — reviewing implies accessing the output
> - **"Regenerate Video"** `<<extends>>` the main flow — it's an optional redo with changed params
> - **Added AI System actor** — Gemini/Veo/FFmpeg are external systems the app depends on
> - **Developer** use cases expanded to reflect actual operational needs (API monitoring, FFmpeg health)

```mermaid
flowchart LR
    subgraph Actors
        PO(("🏠 Property\nOwner"))
        DA(("🔧 Developer\n/ Admin"))
        AI(("🤖 AI Services\n(Gemini/Veo/FFmpeg)"))
    end

    subgraph VistaAI["VistaAI System"]
        direction TB

        subgraph Owner_Actions["Property Owner Actions"]
            UC1([Upload Room Images])
            UC1a([Upload Single Room])
            UC1b([Upload Multi-Room Batch])
            UC2([Set Style Preference])
            UC3([Provide Rough Notes])
            UC4([Review Generated Video])
            UC5([Download Final Tour])
            UC6([Update Narration & Tone])
            UC7([Regenerate Video with\nUpdated Requirements])
        end

        subgraph Admin_Actions["Admin Actions"]
            UC8([User Management\n& Access Control])
            UC9([Monitor API Health])
            UC10([View Video Generation\n& Update Logs])
        end

        subgraph System_Actions["AI Processing"]
            UC11([Analyze Room Type])
            UC12([Generate Staged Image])
            UC13([Generate Transition Video])
            UC14([Generate Narration Script])
            UC15([Generate TTS Audio])
            UC16([Assemble & Stitch\nFinal Video])
        end
    end

    PO --- UC1
    PO --- UC2
    PO --- UC3
    PO --- UC4
    PO --- UC6
    PO --- UC7

    UC1 -.->|"«includes»"| UC1a
    UC1 -.->|"«includes»"| UC1b
    UC4 -.->|"«includes»"| UC5
    UC6 -.->|"«extends»"| UC4
    UC7 -.->|"«extends»"| UC1

    DA --- UC8
    DA --- UC9
    DA --- UC10

    AI --- UC11
    AI --- UC12
    AI --- UC13
    AI --- UC14
    AI --- UC15
    AI --- UC16

    UC1 -.->|triggers| UC11
    UC11 -.->|triggers| UC12
    UC12 -.->|triggers| UC13
    UC2 -.->|feeds into| UC14
    UC3 -.->|feeds into| UC14
    UC14 -.->|triggers| UC15
    UC13 -.->|inputs to| UC16
    UC15 -.->|inputs to| UC16
    UC16 -.->|produces| UC4
```

---

## Corrections Summary

| Handwritten | Corrected | Reason |
|---|---|---|
| Single "Upload Image" | Split into **Single Room** + **Multi-Room Batch** | Both `/generate-room-tour` and `/generate-full-property-tour` endpoints exist |
| *(missing)* | **Set Style Preference** | `preference` is a key input field on every request |
| *(missing)* | **Provide Rough Notes** | `rough_notes` field exists for full property tours |
| "Update Narration, Tone" extends "Review Video" | **extends** is correct ✅ — updating narration optionally extends reviewing | Kept as-is, this relationship makes sense |
| *(missing)* | **AI Services actor** added | Gemini, Veo, FFmpeg are external systems — standard UML practice |
| *(missing)* | **AI Processing use cases** | Shows what the system does internally (analyze, stage, generate, stitch) |
| "Video Generation & Update Log" | Split into **Monitor API Health** + **View Logs** | More granular admin responsibilities |
