import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logics.script_audio import ScriptGenerator
from logics.video_utils import VideoPostProcessor
import glob

def test_pipeline():
    print("=== VistaAI Master Pipeline Internal Test ===")
    
    demo_image = ""
    # Find a sample image
    pngs = glob.glob("uploads/*.png")
    if pngs:
        demo_image = pngs[0]
    else:
        print("No demo images found. Please ensure uploads directory has at least 1 image.")
        return

    print(f"\nUsing Demo Image: {demo_image}")
    
    # 1. Test Script Generation
    print("\n1. Testing Gemini Vision Script Generator...")
    try:
        with open(demo_image, 'rb') as f:
            img = f.read()
        script = ScriptGenerator.generate_master_script([img], "123 Mockingbird Lane", "Spacious layout", "Neobrutalist Bold")
        print(f"PASS: Gemini Output [Length: {len(script)}]:\n{script}")
    except Exception as e:
        print(f"FAIL: Gemini Script Failed: {e}")
        
    # 2. Test Edge-TTS Generation
    print("\n2. Testing Edge-TTS Audio Engine...")
    try:
        out = ScriptGenerator.generate_audio("Welcome to this beautiful neobrutalist property.", "kore", "test_debug")
        if out and os.path.exists(out[0]):
            audio_len = VideoPostProcessor.get_duration(out[0])
            print(f"PASS: Edge-TTS Success: {out[0]} (Duration: {audio_len}s)")
        else:
            print(f"FAIL: Edge-TTS returned empty array.")
    except Exception as e:
        print(f"FAIL: Edge-TTS Failed: {e}")

    # 3. Test FFmpeg Math Animation
    print("\n3. Testing Cinematic Generator Sync...")
    try:
        target_dur = 4.5
        video_out = VideoPostProcessor.generate_cinematic_effect(demo_image, 1, target_dur)
        if video_out and os.path.exists(video_out):
            vid_len = VideoPostProcessor.get_duration(video_out)
            print(f"PASS: Cinematic Generator Success: {video_out} (Duration: {vid_len}s, Target: {target_dur}s)")
        else:
            print(f"FAIL: Cinematic Generator failed generating file.")
    except Exception as e:
        print(f"FAIL: Cinematic Generator Failed: {e}")

    # 4. Test FFmpeg Synthesizer
    print("\n4. Testing Ambient Lofi Synthesizer...")
    try:
        ambient_out = "uploads/test_debug_ambient.mp3"
        out_pad = VideoPostProcessor.generate_ambient_audio(ambient_out, duration=5)
        if out_pad and os.path.exists(out_pad):
            pad_len = VideoPostProcessor.get_duration(out_pad)
            print(f"PASS: Ambient Synth Success: {out_pad} (Duration: {pad_len}s)")
        else:
            print(f"FAIL: Ambient Synth failed.")
    except Exception as e:
        print(f"FAIL: Ambient Synth Failed: {e}")

if __name__ == "__main__":
    test_pipeline()
