# VistaAI — Class Diagram

## As-Drawn (from handwritten sketch)

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

---

## Corrected Version (aligned to actual codebase)

> [!NOTE]
> Corrections made:
> - **User** → **TourRequest**: The system uses a `TourRequest` Pydantic model, not a User class
> - **Image** → **ImageProcessor**: Actual class in `image_processing.py` with `prompt_generate()` and `transform_image()`
> - **Requirements** merged into **TourRequest**: preference and rough_notes are fields on the request
> - **VideoGenerator**: Corrected method names to match `generate_transition()`
> - **AudioScriptGenerator** split into **ScriptGenerator**: Separate class in `script_audio.py` handling both script + TTS
> - **FinalVideo** → **VideoPostProcessor**: Actual class in `video_utils.py` with real method names
> - Added **FastAPI App** as the orchestrator connecting everything

```mermaid
classDiagram
    direction LR

    class TourRequest {
        +List~str~ image_paths
        +str preference
        +str rough_notes
    }

    class ImageProcessor {
        -Client client
        +prompt_generate(image_path) dict
        +transform_image(image_path) dict
    }

    class VideoGenerator {
        -Client client
        +generate_transition(start_image, end_image) str
        -_prepare_image(image_path) Image
    }

    class ScriptGenerator {
        -Client client
        +generate_script(description, preference) dict
        +generate_master_script(room_sequence, notes, preference) dict
        +generate_audio(input_data, voice_name, output_prefix) list
        -wave_file(filename, pcm, channels, rate, sample_width)
        -_clean_json_response(text) str
    }

    class VideoPostProcessor {
        +add_text_overlay(video_path, text, output_path) str
        +combine_video_audio(video_path, audio_path, output_path) str
        +concatenate_with_transitions(video_paths, output_path) str
        +get_duration(file_path) float
        -_check_ffmpeg()
    }

    class FastAPI_App {
        +health_check() dict
        +generate_room_tour(image_path, preference) dict
        +generate_full_property_tour(request) dict
    }

    TourRequest --> FastAPI_App : submitted to
    FastAPI_App --> ImageProcessor : 1. analyze & stage
    FastAPI_App --> VideoGenerator : 2. generate transition
    FastAPI_App --> ScriptGenerator : 3. script & audio
    FastAPI_App --> VideoPostProcessor : 4. assemble & stitch
    ImageProcessor --> VideoGenerator : staged image feeds
    ImageProcessor --> ScriptGenerator : room context feeds
    VideoGenerator --> VideoPostProcessor : raw video
    ScriptGenerator --> VideoPostProcessor : audio file
```
