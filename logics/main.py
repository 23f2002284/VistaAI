from fastapi import FastAPI, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from logics.database import get_db, SessionLocal, engine
from logics import models
from logics.image_processing import ImageProcessor
from logics.video_generator import VideoGenerator
from logics.script_audio import ScriptGenerator
from logics.video_utils import VideoPostProcessor
import os
import shutil

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

@app.post("/generate-room-tour")
async def generate_room_tour(
    file: UploadFile = File(...),
    preference: str = Form("Modern Clean"),
    db: Session = Depends(get_db)
):
    # Backward compatibility endpoint
    return {"status": "success", "message": "Legacy room tour. Use full-property-tour."}

def process_tour_background(request_id: str, mode: str, voice: str):
    db: Session = SessionLocal()
    try:
        req = db.query(models.TourRequest).filter_by(request_id=request_id).first()
        if not req:
            return
            
        rooms = list(req.rooms)
        rooms.sort(key=lambda r: r.sequence_order)
        
        # 1. Master Script Vision & Generation
        try:
            from logics.script_audio import ScriptGenerator
            images_bytes = []
            for room in rooms:
                with open(room.original_image_path, "rb") as f:
                    images_bytes.append(f.read())
            
            master_data = ScriptGenerator.generate_master_script(images_bytes, req.preference, req.rough_notes, "Cinematic")
            master_script = master_data.get("script", "Welcome to this beautifully designed elegant home.")
            keywords = master_data.get("keywords", [])
            
            import re
            sentences = [s.strip() for s in re.split(r'(?<=[.!?]) +', master_script) if s.strip()]
            if len(sentences) < len(rooms):
                sentences += ["Enjoy the view."] * (len(rooms) - len(sentences))
        except Exception as e:
            print("Vision/Scripting error:", e)
            sentences = ["Welcome to this beautiful space."] * len(rooms)
            keywords = []
            
        room_clips = []
        for idx, room in enumerate(rooms):
            original_path = room.original_image_path
            scene_text = sentences[idx] if idx < len(sentences) else "Beautiful."
            room.room_type = keywords[idx] if idx < len(keywords) else "Exclusive Property"
            
            # Step 1: Generate Audio Voiceover First to extract length 
            audio_path_list = ScriptGenerator.generate_audio(scene_text, voice, f"{request_id}_{idx}")
            audio_duration_sec = 4.0
            valid_voice = False
            
            if audio_path_list and os.path.exists(audio_path_list[0]):
                try:
                    audio_duration_sec = VideoPostProcessor.get_duration(audio_path_list[0])
                    valid_voice = True
                except:
                    pass
            
            # Step 2: Generate Video locked precisely to Voiceover length
            if mode == "Premium":
                try:
                    transform_res = ImageProcessor.transform_image(original_path)
                    staged_path = transform_res.get("output_path", original_path)
                    
                    # Instead of forcing Veo to morph reality (hallucinating), feed it the Staged Image 
                    # so the entire video cinematic revolves elegantly around the beautifully transformed aesthetic!
                    transition_path = VideoGenerator.generate_transition(staged_path, staged_path)
                except Exception as ex:
                    print(f"Premium API Error for room {idx}, seamlessly falling back to Basic Engine: {ex}")
                    staged_path = original_path
                    transition_path = VideoPostProcessor.generate_cinematic_effect(original_path, idx, audio_duration_sec)
                    if not transition_path:
                        transition_path = original_path
            else:
                staged_path = original_path
                transition_path = VideoPostProcessor.generate_cinematic_effect(original_path, idx, audio_duration_sec)
                if not transition_path:
                    transition_path = original_path

            overlay_path = f"uploads/{request_id}_{idx}_overlay.mp4"
            VideoPostProcessor.add_text_overlay(transition_path, room.room_type, overlay_path)
            
            # Step 3: Mix the perfectly synced bounds
            final_clip = f"uploads/{request_id}_{idx}_voiced.mp4"
            
            if audio_path_list and os.path.exists(audio_path_list[0]):
                VideoPostProcessor.combine_video_audio(overlay_path, audio_path_list[0], final_clip)
                room_clips.append(final_clip)
            else:
                room_clips.append(overlay_path) # Warning: Only hits if local Disk I/O completely crashes
                
            db.commit()
            
        if len(room_clips) > 1:
            concat_path = f"uploads/{request_id}_concat.mp4"
            VideoPostProcessor.concatenate_videos(room_clips, concat_path)
            
            # Master Ambient Audio Mix
            final_video_path = f"uploads/{request_id}_final.mp4"
            ambient_path = f"uploads/{request_id}_ambient.mp3"
            
            VideoPostProcessor.generate_ambient_audio(ambient_path, duration=len(room_clips)*4)
            VideoPostProcessor.mix_ambient_audio(concat_path, ambient_path, final_video_path)
            
        elif len(room_clips) == 1:
            final_video_path = room_clips[0]
        else:
            final_video_path = ""
            
        if final_video_path:
            final = models.FinalTour(request_id=request_id, output_path=final_video_path)
            db.add(final)
            db.commit()
            
    except Exception as e:
        print(f"Error processing asynchronous pipeline for {request_id}: {e}")
        try:
            # Unlock the UI from endless polling by pushing an exact state signal
            error_req = models.FinalTour(request_id=request_id, output_path="FAILED_GENERATION")
            db.add(error_req)
            db.commit()
        except:
            pass
    finally:
        db.close()

@app.post("/generate-wizard-script")
async def generate_wizard_script(
    address: str = Form(...),
    preference: str = Form("Modern Clean"),
    rough_notes: str = Form(""),
    images: List[UploadFile] = File(...),
):
    try:
        images_bytes = []
        for file in images:
            b = await file.read()
            images_bytes.append(b)
            
        master_data = ScriptGenerator.generate_master_script(images_bytes, address, rough_notes, preference)
        script_text = master_data.get("script", "Failed to decode JSON script.")
        return {"status": "success", "script": script_text}
    except Exception as e:
        print("Script Generation Error:", e)
        return {"status": "error", "message": str(e)}

@app.post("/generate-full-property-tour")
async def generate_full_property_tour(
    background_tasks: BackgroundTasks,
    address: str = Form(...),
    preference: str = Form("Modern Clean"),
    mode: str = Form("Premium"),
    rough_notes: str = Form(""),
    voice: str = Form(""),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    import uuid
    import shutil
    import os
    
    request_id = str(uuid.uuid4())
    tour_request = models.TourRequest(
        request_id=request_id,
        preference=address,
        rough_notes=rough_notes,
        mode=mode
    )
    db.add(tour_request)
    
    # Save the actual files to disk and bind them to the database
    for idx, file in enumerate(images):
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        saved_filename = f"{request_id}_room_{idx}.{file_ext}"
        saved_path = f"uploads/{saved_filename}"
        
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        room = models.Room(
            request_id=request_id,
            sequence_order=idx + 1,
            original_image_path=saved_path,
            room_type="To Be Detected"
        )
        db.add(room)

    db.commit()
    
    background_tasks.add_task(process_tour_background, request_id, mode, voice)
    
    return {"status": "success", "id": request_id, "message": "Multi-image processing initialized for full tour."}

@app.get("/tours")
async def get_tours(db: Session = Depends(get_db)):
    tours = db.query(models.TourRequest).all()
    result = []
    for t in tours:
        status = "Processing"
        video_url = None
        thumbnail_url = None
        
        # Extract thumbnail from the very first room attached to the database architecture
        if t.rooms and len(t.rooms) > 0:
            thumbnail_url = f"http://localhost:8000/{t.rooms[0].original_image_path}"
            
        if t.final_tour:
            if t.final_tour.output_path == "FAILED_GENERATION":
                status = "Failed"
            else:
                status = "Complete"
                video_url = f"http://localhost:8000/{t.final_tour.output_path}"
        result.append({
            "id": t.request_id[:8].upper(),
            "address": t.preference or "No Preference Stated",
            "status": status,
            "date": "Recently",
            "video_url": video_url,
            "thumbnail_url": thumbnail_url
        })
    return result
