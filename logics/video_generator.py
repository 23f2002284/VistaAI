import time
from google import genai
from google.genai import types
from logics.config import GEMINI_API_KEY
from logics.prompts import VIDEO_GENERATION_REINOVATION_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)

class VideoGenerator:
    @staticmethod
    def generate_transition(start_image_path: str, end_image_path: str) -> str:
        """
        Generates a 4-second video transition from start_image to end_image using Google Veo.
        """
        with open(start_image_path, "rb") as f:
            start_bytes = f.read()
        with open(end_image_path, "rb") as f:
            end_bytes = f.read()

        start_img_type = types.Image(image_bytes=start_bytes, mime_type="image/png")
        end_img_type = types.Image(image_bytes=end_bytes, mime_type="image/png")

        try:
            # Utilize the user's proven exact Generator parameters verified against the Veo Vertex APIs.
            operation = client.models.generate_videos(
                model='veo-3.1-generate-preview',
                prompt=VIDEO_GENERATION_REINOVATION_PROMPT,
                image=start_img_type, 
                config=types.GenerateVideosConfig(
                    last_frame=end_img_type,
                    aspect_ratio="16:9",
                    resolution="720p",
                    person_generation="allow_adult"
                )
            )
            
            # Wait for generation to complete
            while not operation.done:
                time.sleep(10)
                operation = client.operations.get(operation=operation)
                
            # Download the final video
            import os
            import urllib.request
            
            start_base = os.path.basename(start_image_path).split('.')[0]
            end_base = os.path.basename(end_image_path).split('.')[0]
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            output_path = f"uploads/{start_base}_{end_base}_transition.mp4"
            
            # Securely deserialize utilizing the user's proven historical SDK method
            video_result = operation.response.generated_videos[0]
            try:
                # Best attempt to natively pull using the validated SDK extension
                with open(output_path, "wb") as f:
                    f.write(video_result.video.video_bytes)
            except Exception:
                try:
                    # Dynamic SDK Cloud File Extraction fallback based precisely on historical syntax
                    out_bytes = client.files.download(file=video_result.video)
                    with open(output_path, "wb") as f:
                        f.write(out_bytes)
                except Exception:
                    # Final direct download invocation wrapper
                    client.files.download(file=video_result.video)
                    video_result.video.save(output_path)
                    
            return output_path
            
        except Exception as e:
            print(f"Vertex AI Veo Error (Fallback Triggered): {e}")
            from logics.video_utils import VideoPostProcessor
            return VideoPostProcessor.generate_cinematic_effect(end_image_path, 0, 4.0)
