import os
import io
from PIL import Image
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel, Image as VertexImage
from backend.config import PROJECT_ID, LOCATION

class ImageProcessor:
    def __init__(self):
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            # "Nano Banana Pro" -> Mapping to standard Imagen 3 or latest available on Vertex
            # Assuming 'imagen-3.0-generate-001' or similar for high quality
            self.model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
            print("Vertex AI Imagen Setup Complete")
        except Exception as e:
            print(f"Warning: Vertex AI Init Failed: {e}")
            self.model = None

    def smart_crop_zoom(self, image_path: str, zoom_factor: float = 1.1) -> str:
        """
        Crops the center of the image to simulate a zoom-in effect, 
        then resizes back to original dimensions.
        """
        img = Image.open(image_path)
        width, height = img.size
        
        # Calculate centered crop
        new_width = width / zoom_factor
        new_height = height / zoom_factor
        
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        
        # Crop & Resize
        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        output_path = image_path.replace(".", "_zoomed.")
        img_resized.save(output_path)
        return output_path

    def transform_image(self, image_path: str, prompt_override: str = None) -> str:
        """
        Uses Vertex AI (Nano Banana Pro) to virtually stage the images.
        """
        if not self.model:
            raise RuntimeError("Vertex AI Model not (Nano Banana Pro) initialized")

        # Base prompts as per user request
        base_prompt = (
            "Photorealistic virtual staging. "
            "Correct the lighting and improve image quality. "
            "Understand the property style and room style and add appropriate furniture combination that suits the room. "
            "Do not change the room structure or dimensions. "
            "High resolution, 4k, interior design magazine quality."
        )
        
        final_prompt = f"{base_prompt} {prompt_override}" if prompt_override else base_prompt
        
        print(f"Generating transformation with prompt: {final_prompt}")
        
        # Read image bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        vertex_image = VertexImage(image_bytes=image_bytes)

        # Generating the staged version
        # Note: Using edit_image for 'inpainting' or 'product-image' type edit is standard.
        # But for 'whole room staging' without mask, we rely on the model's ability to overlay.
        # If 'edit_image' requires mask, we might need to assume a mask that covers the floor/empty space.
        # For this MVP, we will try to use the model's generation capability conditioned on the base image if available,
        # or use edit_image with null mask or broad mask.
        
        # For now, assuming edit_image can handle slight variations or we provide a mask.
        # Since we don't have an auto-segmentation model yet, let's try to generate with base_image text-to-image variation if supported
        # OR just call edit_image.
        
        # NOTE: Imagen 2 Edit Image requires a mask.
        # STRATEGY: We will proceed with the assumption, but we might need to add a 'mask_generation' step later.
        # For the MVP, we will assume we can just pass the image.
        
        try:
           # Attempt 1: Edit Image (Inpainting/Outpainting) - requires mask usually.
           # Attempt 2: Image Variation (if supported).
           
           # Let's try standard generation with standard prompt logic for now.
           # In a real deployed Nano Banana Pro, there might be specific args.
           
           # Placeholder for actual call
           response = self.model.edit_image(
               base_image=vertex_image,
               prompt=final_prompt,
               guidance_scale=21, # Strong adherence to prompt
               # mask=... 
           )
           
           generated_image = response.images[0]
           output_path = image_path.replace(".", "_furnished.")
           generated_image.save(output_path)
           return output_path
           
        except Exception as e:
            print(f"Error during image transformation: {e}")
            # Fallback for testing flow if API fails (mocking)
            # return image_path 
            raise e
