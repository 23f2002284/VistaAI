import sys
import os

# Add project root to sys.path to allow importing backend module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logics import ImageProcessor

if __name__ == "__main__":
    image_processor = ImageProcessor()
    # print(image_processor.prompt_generate("uploads/image.png"))
    image_processor.transform_image("uploads/image.png")
