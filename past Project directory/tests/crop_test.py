import sys
import os

# Add project root to sys.path to allow importing backend module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.image_processor import ImageProcessor

# Initialize processor
processor = ImageProcessor()
# Call method
processor.smart_crop_zoom("uploads/image.png")
