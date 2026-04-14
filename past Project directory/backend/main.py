import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from backend.config import PROJECT_ID
from backend.image_processor import ImageProcessor
from backend.video_generator import VideoGenerator
from backend.script_audio import ScriptGenerator, AudioGenerator
from backend.media_assembler import MediaAssembler

app = FastAPI(title="VistaAI MVP")

# Initialize modules
# Note: In production, these might be singletons or dependency injected
img_proc = ImageProcessor()
vid_gen = VideoGenerator()
script_gen = ScriptGenerator()
audio_gen = AudioGenerator()
assembler = MediaAssembler()

class ProcessResponse(BaseModel):
    status: str
    original_image: str
    transformed_image: str
    video_transition: str
    script: str
    audio: str
    final_output: str

@app.get("/")
def health_check():
    return {"status": "running", "project": PROJECT_ID}

@app.post("/process_property", response_model=ProcessResponse)
async def process_property(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    voice_preference: str = Form("Natural"), # Natural or Emotional
    script_style: str = Form("Standard real estate marketing"),
    zoom_factor: float = Form(1.2)
):
    """
    Full pipeline execution:
    1. Ingest Image
    2. Smart Crop & Transform (Virtual Staging)
    3. Generate Zoom/Transition Video
    4. Generate Script & Audio
    5. Assemble Final Video
    """
    
    # 1. Save uploaded file
    file_location = f"temp_{image.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(image.file, file_object)
        
    print(f"Processing image: {file_location}")
    
    # Run pipeline (Synchronous for MVP simplicity, usually async/background)
    
    try:
        # Step 1: Transformation & Zoom
        # Flow: Original -> Crop(Zoom) -> Transform (Furnish)
        # We assume the 'Transformed Image' is the Staged ZOOMED version.
        zoomed_path = img_proc.smart_crop_zoom(file_location, zoom_factor=zoom_factor)
        transformed_path = img_proc.transform_image(zoomed_path)
        
        # Step 2: Video Generation
        # Transition from Original (Wide) -> Transformed (Zoomed Staged)
        # We pass both to generator
        transition_video_path = vid_gen.generate_transition(start_image_path=file_location, end_image_path=transformed_path)
        
        # Step 3: Script & Audio
        # Generate script based on the Transformed image (showing the furniture)
        script_text = script_gen.generate_script(transformed_path, preference=script_style)
        audio_path, duration = audio_gen.generate_audio(script_text, voice_type=voice_preference)
        
        # Step 4: Assembly
        # Sync video length to audio length
        final_output_path = f"final_{os.path.splitext(image.filename)[0]}.mp4"
        assembler.assemble_final_video(transition_video_path, audio_path, output_path=final_output_path)
        
        return ProcessResponse(
            status="success",
            original_image=file_location,
            transformed_image=transformed_path,
            video_transition=transition_video_path,
            script=script_text,
            audio=audio_path,
            final_output=final_output_path
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ProcessResponse(
            status=f"error: {str(e)}",
            original_image=file_location,
            transformed_image="",
            video_transition="",
            script="",
            audio="",
            final_output=""
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
