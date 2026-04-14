# 🎬 VistaAI: Cinematic Real Estate AI Pipeline

![VistaAI Premium](https://img.shields.io/badge/System-Premium-00E5FF?style=for-the-badge&logo=google-cloud&logoColor=white)
![Python](https://img.shields.io/badge/Backend-FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React_Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![AI Models](https://img.shields.io/badge/AI-Gemini_%7C_Veo-orange?style=for-the-badge&logo=google-gemini&logoColor=white)

**VistaAI** is an elite, fully-hardenend AI video synthesis platform. It transforms standard architectural photos into high-production-value property tours using ultra-modern Vision and Generative AI.

---

## 💎 The Midnight Aesthetic
VistaAI features a world-class **Midnight Glass & Electric Cyan** UI, engineered with true glassmorphism, glowing volumetric shadows, and fluid micro-animations. It's built for those who value both technical precision and visual excellence.

---

## 🛠️ Technical Evolution (The Hardened Pipeline)

The VistaAI pipeline is a self-healing asynchronous engine designed to handle the complexities of multimodal AI generation.

### 🏛️ System Architecture
```mermaid
graph LR
    subgraph Frontend["🎨 Frontend (Vite + React)"]
        Dashboard["Bento-Grid Overview"]
        Wizard["Tour Creation Wizard"]
        Projects["Project Management"]
    end

    subgraph Backend["⚙️ Backend (FastAPI)"]
        API["FastAPI Orchestrator"]
        DB[(SQLite / SQLAlchemy)]
        Worker["Async Pipeline Worker"]
    end

    subgraph AI["🤖 AI Engine (Vertex API)"]
        Gemini["Gemini 2.5/3.1 (Analysis & Vision)"]
        Veo["Veo 3.1 (Transition Synthesis)"]
        TTS["Edge-TTS (Neural Voiceover)"]
        FFmpeg["FFmpeg Studio (Post-Processing)"]
    end

    Frontend <--> API
    API <--> DB
    API --> Worker
    Worker --> AI
```

---

## 🔄 The Cinematic Pipeline Flow
VistaAI doesn't just "make videos"—it orchestrates a multi-stage creative process.

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

![Activity Diagram](file:///c:/Users/praty/Desktop/SE%20Project/diagrams/activity%20diagram.jpeg)

---

## 🧱 Data Orchestration (ERD)
The persistence layer manages project lifecycles, ensuring a "Single Source of Truth" for every generated property asset.

```mermaid
erDiagram
    TOUR_REQUEST ||--o{ ROOM : contains
    TOUR_REQUEST ||--o| FINAL_TOUR : produces
    
    TOUR_REQUEST {
        string request_id PK
        string address
        string preference
        string rough_notes
        string status
        datetime created_at
    }
    
    ROOM {
        int id PK
        string request_id FK
        string original_path
        string staged_path
        string room_type
        string transition_video_path
        string audio_path
    }
    
    FINAL_TOUR {
        int id PK
        string request_id FK
        string output_path
        float duration
    }
```

## 🏗️ System Modeling (UML)

To ensure technical maintainability, VistaAI is documented with full UML specifications.

### 🧵 Sequence Diagram (Orchestration Logic)
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

![Sequence Diagram](file:///c:/Users/praty/Desktop/SE%20Project/diagrams/sequence%20diagram.jpeg)

### ⚓ Class Diagram (System Hierarchy)
```mermaid
classDiagram
    direction LR

    class User {
        +UUID vid
        +String name
        +String joined
        +upload_image()
        +upload_narration()
        +upload_tone()
    }

    class Image {
        +String image_address
        +String shape
        +transform()
        +validate()
    }

    class Requirements {
        +String narration
        +String tone
        +validate()
    }

    class VideoGenerator {
        +String original_image
        +String transformed_image
        +generate_video()
    }

    class AudioScriptGenerator {
        +String video_gen
        +String narration
        +String script
        +String sequence_json
        +script_gen()
        +audio_gen()
    }

    class FinalVideo {
        +String generated_video_address
        +String response
        +stitch_content()
        +update_content()
    }

    User --> Image : uploads
    User --> Requirements : uploads
    Image --> VideoGenerator : processed by
    VideoGenerator --> AudioScriptGenerator : used by
    Requirements --> AudioScriptGenerator : used by
    AudioScriptGenerator --> FinalVideo : stitched by
```

![Class Diagram](file:///c:/Users/praty/Desktop/SE%20Project/diagrams/class%20diagram.jpeg)

### 👥 Use Case Diagram
```mermaid
flowchart LR
    subgraph Actors
        PO["Property\nOwner"]
        DA["Developer\n/ Admin"]
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

![Use Case Diagram](file:///c:/Users/praty/Desktop/SE%20Project/diagrams/use%20case.jpeg)

---

## 📂 Project Structure

| Module | Responsibility |
|---|---|
| `logics/main.py` | FastAPI entrypoint and Orchestration logic. |
| `logics/image_processing.py` | Vision analysis and Nano Banana Staging (Gemini 3.1). |
| `logics/video_generator.py` | Cinematic video synthesis (Veo 3.1). |
| `logics/script_audio.py` | Script generation and Edge-TTS voice synthesis. |
| `logics/video_utils.py` | FFmpeg assembly, Text Overlays, and Concat Studio. |
| `frontend/src/App.jsx` | Core React Routing and Theme Switching. |
| `frontend/src/index.css` | The "Midnight Glass" Design System tokens. |

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- FFmpeg (Installed on system PATH)

### 2. Environment Setup
Create a `.env` in the root directory:
```bash
GEMINI_API_KEY=your_google_ai_studio_api_key
```

### 3. Backend Deployment
```bash
# Activate your venv
pip install -r requirements.txt
uvicorn logics.main:app --reload
```

### 4. Frontend Deployment
```bash
cd frontend
npm install
npm run dev
```

---

## 🛡️ Reliability Features
- **Self-Healing Fallbacks**: If the cloud API fails, the pipeline automatically switches to local "Fast Styler" mode to ensure tour completion.
- **Infinite Loop Defense**: Explicit temporal capping on all FFmpeg mixes prevents encoder hangs.
- **Async Polling**: The frontend uses reactive status polling to provide real-time updates without page refreshes.

---
> [!NOTE] 
> VistaAI is currently in **Premium MVP v1.0**. All generation credits are managed via the Vertex AI preview program.