import time
import os
import vertexai
from vertexai.preview.vision_models import Image, VideoGenerationModel
from backend.config import PROJECT_ID, LOCATION

class VideoGenerator:
    def __init__(self):
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            # Using 'imagen-video-generation-001' or 'veo-001' if available
            self.model = VideoGenerationModel.from_pretrained("imagen-video-generation-001")
            print("Vertex AI Video (Veo/Imagen) Setup Complete")
        except Exception as e:
            print(f"Warning: Vertex AI Video Init Failed: {e}")
            self.model = None

    def generate_transition(self, start_image_path: str, end_image_path: str = None) -> str:
        """
        Generates a transition video.
        Uses the start image (Empty room) to generate a video where furniture pops in.
        """
        if not self.model:
            raise RuntimeError("Video Model not initialized")

        print(f"Loading start image: {start_image_path}")
        with open(start_image_path, "rb") as f:
            start_img_bytes = f.read()
        
        start_image = Image(image_bytes=start_img_bytes)

        # User specified prompt
        prompt = (
            "Each pieces of furniture pops up, rotates and falls into places one by one. "
            "The camera has super smooth forward motion. "
            "Cinematic, 4k, photorealistic, interior design."
        )
        
        print(f"Generating video with prompt: {prompt}")

        try:
            # Note: If API supports 'end_image' (interpolation), we would pass it here.
            # Currently standard Vertex Image-to-Video takes 'image'.
            # We assume 'image' is the starting point.
            
            response = self.model.generate_video(
                video_prompt=prompt,
                image=start_image,
                aspect_ratio="16:9",
                add_audio=False,
                # frames=80 # Optional control
            )
            
            # Wait for operation if needed, but generate_video might be sync or return job
            # The SDK usually creates a polling job.
            
            output_path = start_image_path.replace(".", "_transition.")
            if not output_path.endswith(".mp4"):
                output_path += "mp4"
                
            # Response handling usually involves writing bytes
            if hasattr(response, "video_bytes"):
                 with open(output_path, "wb") as f:
                    f.write(response.video_bytes)
            else:
                # If response is a job/operation, we might need to fetch result
                # For Vertex Preview, it often returns a generated video object directly
                 with open(output_path, "wb") as f:
                    f.write(response[0].video_bytes) # Often a list of videos

            print(f"Video saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"Error generating video: {e}")
            raise e
