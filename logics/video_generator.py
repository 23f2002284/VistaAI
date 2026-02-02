from google import genai
import time
import os
from google.genai import types
from logics.config import GEMINI_API_KEY
from logics.prompts import (
    VIDEO_TRANSITION_PROMPT,
    VIDEO_GENERATION_REINOVATION_PROMPT
)

class VideoGenerator:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
    
    def _prepare_image(self, image_path):
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        return types.Image(
            image_bytes=image_bytes,
            mime_type="image/png" # Assuming PNG based on previous steps, or detect
        )

    def generate_transition(self, start_image_path, end_image_path):
        try:
            # Prepare inputs ensuring they map to the correct API expectations
            start_img = self._prepare_image(start_image_path)
            end_img = self._prepare_image(end_image_path)

            operation = self.client.models.generate_videos(
                model = "veo-3.1-generate-preview", # will change the model
                prompt = VIDEO_GENERATION_REINOVATION_PROMPT,
                image = start_img,
                config = types.GenerateVideosConfig(
                    last_frame = end_img,
                    aspect_ratio = "16:9",
                    resolution="720p",
                    durationSeconds="4",
                    personGeneration = "allow_adult"
                )
            )
            # Poll the operation status until the video is ready.
            while not operation.done:
                print("Waiting for video generation to complete...")
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
            # Download and save
            video_result = operation.response.generated_videos[0]
            
            # Robust path handling
            start_base = os.path.splitext(os.path.basename(start_image_path))[0]
            end_base = os.path.splitext(os.path.basename(end_image_path))[0]
            filename = f"{start_base}_{end_base}_transition.mp4"
            filepath = os.path.join("uploads", filename)
            
            # Ensure directory exists
            os.makedirs("uploads", exist_ok=True)
            
            # Download the generated video.
            self.client.files.download(file=video_result.video)
            video_result.video.save(filepath)
                
            return filepath
        except Exception as e:
            print(f"Error generating transition: {e}")
            raise e

        # Still have to fix the video length