import sys
import os

# Add project root to sys.path to allow importing backend module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logics import VideoGenerator

if __name__ == "__main__":
    video_generator = VideoGenerator()
    video_generator.generate_transition("uploads/image.png", "uploads/image_transformed.png")