from fastapi.testclient import TestClient
import sys
import os
import shutil

# Add project root to sys.path to allow importing backend module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logics.main import app
client = TestClient(app)

def test_generate_room_tour():
    # Setup: Ensure sample image exists
    img_path = "uploads/image.png"
    if not os.path.exists(img_path):
        print(f"Skipping test: {img_path} not found.")
        return

    # Check if ffmpeg is available
    if shutil.which("ffmpeg") is None:
        print("Skipping test: FFmpeg not found.")
        return
        
    print(f"Testing generate_room_tour with {img_path}...")
    
    # We pass image_path as a query param as per the endpoint definition
    # Note: In a real scenario, we might upload the file, but here the API expects a local path.
    response = client.post(f"/generate-room-tour?image_path={img_path}&user_preference=Modern+Bohemian")
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"Room Type: {data.get('room_type')}")
        print(f"Video Path: {data.get('final_video')}")
        
        # Verify output exists
        if os.path.exists(data.get('final_video')):
            print("Verified: Final video file exists.")
        else:
            print("Error: Video file reported but not found on disk.")
    else:
        print(f"Failed with status {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_generate_room_tour()
