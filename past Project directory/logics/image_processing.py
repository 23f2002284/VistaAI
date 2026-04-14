from google import genai
from google.genai import types
from PIL import Image
import os
from logics.config import GEMINI_API_KEY
from logics.prompts import (
    IMAGE_EDIT_PROMPT_GENERATION_PROMPT,
    TRANSFORMED_IMAGE_GENERATION_PROMPT
)
from pydantic import BaseModel

class ImageProcessor:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def prompt_generate(self, image_path) -> dict:
        try:
            image = Image.open(image_path)
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    image, 
                    IMAGE_EDIT_PROMPT_GENERATION_PROMPT,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            import json
            return json.loads(response.text)
        except Exception as e:
            print(f"Error generating prompt: {e}")
            raise e
    
    def transform_image(self, image_path):
        try:
            image = Image.open(image_path)
            # Step 1: Analyze & Get Prompt
            analysis_result = self.prompt_generate(image_path)
            prompt = analysis_result.get("staging_prompt", "")
            room_type = analysis_result.get("room_type", "Room")
            
            print(f"Detected Room: {room_type}")

            # Step 2: Generate Image using the prompt
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image", # Keep this if it's the valid model for image gen
                contents=[
                    image, 
                    TRANSFORMED_IMAGE_GENERATION_PROMPT.format(PROMPT_FROM_PREVIOUS_STEP=prompt)
                ]
            )
            saved_path = None
            for part in response.parts:
                if part.text is not None:
                    print(part.text)
                elif part.inline_data is not None:
                    image_out = part.as_image()
                    # Robust path handling
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    saved_path = f"uploads/{base_name}_transformed.png"
                    image_out.save(saved_path)
            
            return {
                "room_type": room_type,
                "output_path": saved_path
            }
        except Exception as e:
            print(f"Error transforming image: {e}")
            raise e