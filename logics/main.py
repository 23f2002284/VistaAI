from logics.image_processing import ImageProcessor
from logics.script_audio import ScriptGenerator
from logics.video_generator import VideoGenerator
from logics.video_utils import VideoPostProcessor
from fastapi import FastAPI, HTTPException
import os

app = FastAPI(title="VistaAI", description="VistaAI is a real estate video generation API", version="1.0.0")

img_proc = ImageProcessor()
script_gen = ScriptGenerator()
vid_gen = VideoGenerator()
post_proc = VideoPostProcessor()

@app.get("/")
def health_check():
    return {"status": "running", "project": "VistaAI"}

@app.post("/generate-room-tour")
def generate_room_tour(image_path: str, user_preference: str = "Modern Minimalist"):
    """
    Full pipeline:
    1. Analyze & Transform Image (Before -> After) -> Get Room Type
    2. Generate Video Transition (Before -> After)
    3. Generate Audio Script & Audio File (Synced to Room Type)
    4. Post-Process: Merge Audio + Video + Add Title Overlay
    """
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"Image {image_path} not found")

    try:
        # 1. Image Transformation & Analysis
        print("Step 1: Transforming Image & Analyzing Room...")
        transform_result = img_proc.transform_image(image_path)
        
        room_type = transform_result.get("room_type", "Unknown Room")
        transformed_image_path = transform_result.get("output_path")
        
        if not transformed_image_path:
             raise HTTPException(status_code=500, detail="Image transformation failed to produce output.")

        print(f"Detected: {room_type}")

        # 2. Video Generation (Transition)
        print("Step 2: Generating Video Transition...")
        raw_video_path = vid_gen.generate_transition(
            start_image_path=image_path,
            end_image_path=transformed_image_path
        )
        
        # 3. Audio Generation
        print("Step 3: Generating Audio...")
        # Create a single scene plan for this room
        tour_plan = {
            "tour_plan": [
                {
                    "sequence_id": 1,
                    "scene_name": room_type,
                    "narration_text": f"Welcome to this renovated {room_type}, styled in a {user_preference} theme." # Fallback or dynamic
                }
            ]
        }
        
        # Or better: Ask script_gen to generate the text properly based on the analysis
        # For this MVP, let's use the property description logic
        script_data = script_gen.generate_script(
            property_description=f"A {room_type} that has been virtually staged.",
            preference=user_preference
        )
        # Use the generated script if available, else fallback
        if script_data.get("tour_plan"):
             # override the simple one
             # ensure we only take the first scene for this single image pipeline
             first_scene = script_data["tour_plan"][0]
             first_scene["scene_name"] = room_type # Ensure consistency
             tour_plan["tour_plan"] = [first_scene]

        audio_files = script_gen.generate_audio(tour_plan, output_prefix=f"audio_{room_type.replace(' ', '_')}")
        audio_path = audio_files[0] if audio_files else None

        # 4. Post Processing
        print("Step 4: Post-Processing (Merge & Overlay)...")
        final_video_path = f"uploads/final_{room_type.replace(' ', '_')}.mp4"
        temp_video_path = f"uploads/temp_{room_type.replace(' ', '_')}.mp4"
        
        # A. Add Text Overlay to Raw Video first
        post_proc.add_text_overlay(
            video_path=raw_video_path,
            text=room_type,
            output_path=temp_video_path
        )
        
        # B. Merge with Audio
        if audio_path:
            post_proc.combine_video_audio(
                video_path=temp_video_path,
                audio_path=audio_path,
                output_path=final_video_path
            )
        else:
            # Fallback if no audio
            os.rename(temp_video_path, final_video_path)

        return {
            "status": "success",
            "room_type": room_type,
            "final_video": final_video_path
        }

    except Exception as e:
        print(f"Pipeline Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
from typing import List

class TourRequest(BaseModel):
    image_paths: List[str]
    preference: str = "Modern Minimalist"
    rough_notes: str = ""

@app.post("/generate-full-property-tour")
def generate_full_property_tour(request: TourRequest):
    """
    Orchestrates a multi-room tour:
    1. Processing multiple images.
    2. Generating a cohesive story script.
    3. Creating individual clips with titles and audio.
    4. Stitching them into one master video.
    """
    if not request.image_paths:
        raise HTTPException(status_code=400, detail="No images provided")

    processed_rooms = []
    
    try:
        # Phase 1: Image Analysis & Transformation
        print("Phase 1: Analyzing & Transforming Images...")
        for img_path in request.image_paths:
            if not os.path.exists(img_path):
                print(f"Skipping missing image: {img_path}")
                continue
            
            # Transform
            res = img_proc.transform_image(img_path)
            processed_rooms.append({
                "original_path": img_path,
                "transformed_path": res["output_path"],
                "room_type": res.get("room_type", "Room"),
                "sequence_id": len(processed_rooms) + 1
            })

        if not processed_rooms:
            raise HTTPException(status_code=400, detail="No valid images processed")

        # Phase 2: Video Generation (Parallelizable in future, sequential for now)
        print("Phase 2: Generating Transition Videos...")
        for room in processed_rooms:
            vid_path = vid_gen.generate_transition(
                start_image_path=room["original_path"],
                end_image_path=room["transformed_path"]
            )
            room["raw_video"] = vid_path
        
        # Phase 3: Master Script Generation
        print("Phase 3: Generating Cohesive Narrative...")
        room_sequence = [r["room_type"] for r in processed_rooms]
        script_data = script_gen.generate_master_script(
            room_sequence=room_sequence, 
            rough_notes=request.rough_notes,
            preference=request.preference
        )
        
        # Parse script: Expecting "tour_script" list matching sequence
        # We try to match by index
        tour_script = script_data.get("tour_script", [])
        
        # Phase 4: Per-Room Assembly (Audio + Overlay + Merge)
        print("Phase 4: Assembling Room Clips...")
        final_clips = []
        
        import uuid
        request_id = str(uuid.uuid4())[:8]

        for i, room in enumerate(processed_rooms):
            # Get script for this room
            narration = ""
            if i < len(tour_script):
                narration = tour_script[i].get("narration_text", "")
            else:
                narration = f"Here is the {room['room_type']}." # Fallback

            # Generate Audio
            # We treat each room as a single item for audio gen to get a specific file
            audio_files = script_gen.generate_audio(
                input_data=narration, 
                output_prefix=f"uploads/audio_{request_id}_{i}"
            )
            audio_path = audio_files[0] if audio_files else None
            
            # Post-Process
            # 1. Overlay Title
            temp_overlay_path = f"uploads/temp_overlay_{request_id}_{i}.mp4"
            post_proc.add_text_overlay(
                video_path=room["raw_video"],
                text=room["room_type"],
                output_path=temp_overlay_path
            )
            
            # 2. Merge Audio
            final_clip_path = f"uploads/clip_{request_id}_{i}_{room['room_type'].replace(' ', '_')}.mp4"
            if audio_path:
                post_proc.combine_video_audio(
                    video_path=temp_overlay_path,
                    audio_path=audio_path,
                    output_path=final_clip_path
                )
            else:
                os.rename(temp_overlay_path, final_clip_path)
            
            final_clips.append(final_clip_path)

        # Phase 5: Concatenation
        print("Phase 5: Stitching Full Tour with Transitions...")
        master_output = f"uploads/final_property_tour_{request_id}.mp4"
        post_proc.concatenate_with_transitions(final_clips, master_output)
        
        return {
            "status": "success",
            "full_tour_path": master_output,
            "clips": final_clips
        }

    except Exception as e:
        print(f"Pipeline Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))