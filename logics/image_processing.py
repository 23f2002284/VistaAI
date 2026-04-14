import os
import json
from google import genai
from google.genai import types
from PIL import Image
from logics.config import GEMINI_API_KEY
from logics.prompts import IMAGE_EDIT_PROMPT_GENERATION_PROMPT, TRANSFORMED_IMAGE_GENERATION_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)

class ImageProcessor:
    @staticmethod
    def prompt_generate(image_path: str) -> dict:
        """
        Analyzes the room and selects a style.
        Returns: {room_type, visual_style, description, staging_prompt}
        """
        img = Image.open(image_path)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, IMAGE_EDIT_PROMPT_GENERATION_PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def transform_image(image_path: str) -> dict:
        """
        Transforms the image by adding furniture and preserving architecture.
        """
        prompt_data = ImageProcessor.prompt_generate(image_path)
        if not prompt_data or "staging_prompt" not in prompt_data:
            raise Exception("Failed to generate staging prompt.")

        staging_prompt = prompt_data["staging_prompt"]
        room_type = prompt_data.get("room_type", "Room")

        formatted_prompt = TRANSFORMED_IMAGE_GENERATION_PROMPT.format(
            PROMPT_FROM_PREVIOUS_STEP=staging_prompt
        )
        
        img = Image.open(image_path)
        
        # Using Nano Banana Pro (Gemini 3 Pro Image) via generate_content endpoint
        response = client.models.generate_content(
            model='gemini-3.1-flash-image-preview',
            contents=[img, formatted_prompt],
        )

        output_path = f"uploads/{os.path.basename(image_path).split('.')[0]}_transformed.png"
        
        # Traverse multimodal response array for the pure image binary matrix
        if response.parts:
            for part in response.parts:
                if part.inline_data is not None:
                    final_image = part.as_image()
                    final_image.save(output_path)
                    break
        
        return {
            "room_type": room_type,
            "output_path": output_path,
            "staging_prompt": staging_prompt
        }
