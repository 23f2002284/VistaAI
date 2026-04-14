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
    Start(( )) --> Upload([User Submits Images + Preferences])
    Upload --> Analysis([Gemini Vision: Detect Room Type & Vibe])
    Analysis --> Staging([Nano-Banana-Pro: Virtual Interior Design])
    Staging --> Video([Veo 3.1: Synthesis of Cinematic Transitions])
    Video --> Audio([Narration Script & Neural TTS Engine])
    Audio --> Assemble([FFmpeg: Text Overlays + Voice Mix])
    Assemble --> Final([Master Tour Concatenation with Crossfades])
    Final --> End((◉))

    style Start fill:#000,stroke:#000
    style End fill:#000,stroke:#333
    style Analysis fill:#bfdbfe,stroke:#2563eb
    style Staging fill:#bfdbfe,stroke:#2563eb
    style Video fill:#bbf7d0,stroke:#16a34a
    style Audio fill:#fef08a,stroke:#ca8a04
    style Assemble fill:#fbcfe8,stroke:#db2777
    style Final fill:#d9f99d,stroke:#65a30d
```

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
    actor PO as 🏠 Property Owner
    participant API as FastAPI Server
    participant IMG as ImageProcessor
    participant VID as VideoGenerator
    participant SCR as ScriptGenerator
    participant PP as VideoPostProcessor (FFmpeg)

    PO->>API: POST /generate-full-property-tour
    Note over API: Step 1: Vision Analysis & Staging
    API->>IMG: transform_image(image_path)
    IMG-->>API: {room_type, staged_image_path}
    
    Note over API: Step 2: Video Transition Synthesis
    API->>VID: generate_transition(staged, staged)
    VID-->>API: transition_video.mp4
    
    Note over API: Step 3: Script & Audio Production
    API->>SCR: generate_master_script()
    SCR->>SCR: TTS Synthesis via Edge-TTS
    SCR-->>API: narration_audio.mp3
    
    Note over API: Step 4: Final Studio Assembly
    API->>PP: add_text_overlay()
    API->>PP: combine_video_audio()
    API->>PP: concatenate_with_transitions()
    PP-->>API: final_tour.mp4
    API-->>PO: Return Tour URL
```

### ⚓ Class Diagram (System Hierarchy)
```mermaid
classDiagram
    direction LR
    class TourRequest {
        +List~str~ image_paths
        +str preference
        +str rough_notes
    }
    class ImageProcessor {
        +prompt_generate(image_path)
        +transform_image(image_path)
    }
    class VideoGenerator {
        +generate_transition(start, end)
    }
    class ScriptGenerator {
        +generate_master_script()
        +generate_audio()
    }
    class VideoPostProcessor {
        +add_text_overlay()
        +combine_video_audio()
        +concatenate_with_transitions()
    }
    
    TourRequest --> ImageProcessor
    ImageProcessor --> VideoGenerator
    VideoGenerator --> VideoPostProcessor
    ScriptGenerator --> VideoPostProcessor
```

### 👥 Use Case Diagram
```mermaid
flowchart LR
    PO(("🏠 Property Owner"))
    AI(("🤖 AI Services"))
    
    subgraph VistaAI
        UC1([Upload Images])
        UC2([Select Style Preference])
        UC3([Generate Video Tour])
        UC4([Download MP4 Asset])
        UC5([Analyze Room])
        UC6([Generate Voiceover])
    end
    
    PO --- UC1
    PO --- UC2
    PO --- UC3
    UC3 --- UC4
    AI --- UC5
    AI --- UC6
    UC3 -.->|includes| UC1
    UC3 -.->|includes| UC5
```

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