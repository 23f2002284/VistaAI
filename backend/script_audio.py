import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import texttospeech
from backend.config import PROJECT_ID, LOCATION

class ScriptGenerator:
    def __init__(self):
        try:
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            self.model = GenerativeModel("gemini-1.5-flash")
            print("Vertex AI Gemini Setup Complete")
        except Exception as e:
            print(f"Warning: Gemini Init Failed: {e}")
            self.model = None

    def generate_script(self, image_path: str, preference: str = "Standard real estate marketing") -> str:
        """
        Generates a video script based on the image content and user preference.
        """
        if not self.model:
            raise RuntimeError("Gemini Model not initialized")

        with open(image_path, "rb") as f:
            image_bytes = f.read()

        image_part = Part.from_data(image_bytes, mime_type="image/jpeg") # Assuming JPEG/PNG
        
        prompt = (
            f"You are a professional real estate copywriter. "
            f"Write a short, engaging video script (narration) for this room. "
            f"The script needs to match this style preference: '{preference}'. "
            f"Keep it concise, suitable for a 10-15 second video clip. "
            f"Focus on the lighting, furniture, and atmosphere shown in the image (or implied if empty)."
            f"Do not include scene directions, just the spoken text."
        )

        response = self.model.generate_content([image_part, prompt])
        return response.text.strip()

class AudioGenerator:
    def __init__(self):
        try:
            self.client = texttospeech.TextToSpeechClient()
            print("Google Cloud TTS Client Setup Complete")
        except Exception as e:
            print(f"Warning: Google Cloud TTS Init Failed: {e}")
            self.client = None

    def generate_audio(self, text: str, voice_type: str = "Natural") -> tuple[str, float]:
        """
        Generates audio from text using simple Google Cloud TTS.
        Returns: (audio_file_path, duration_seconds)
        """
        if not self.client:
            raise RuntimeError("TTS Client not initialized")

        # Configure voice
        # "Natural" -> Journey or Neural2. "Emotional" -> Specific Journey voices?
        # Journey voices are usually "en-US-Journey-D" etc.
        voice_name = "en-US-Journey-F" if voice_type == "Emotional" else "en-US-Journey-O" # 'O' is often calm/natural

        input_text = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name,
            # ssml_gender=texttospeech.SsmlVoiceGender.FEMALE 
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0 # 1.0 is normal speed
        )

        response = self.client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        # Save audio
        output_path = "generated_audio.mp3"
        with open(output_path, "wb") as out:
            out.write(response.audio_content)

        # Calculate duration using moviepy or pydub (since TTS API doesn't return duration directly)
        # Or simple estimate/parse header.
        # We will use another lib later (Assembler) to get exact duration, 
        # but let's try to get it here if possible.
        # We can use 'mutagen' or just return path and let Assembler handle it.
        # But user requested "Audio Duration" logic here.
        # Let's import moviepy.editor AudioFileClip to get duration safely.
        
        duration = 0.0
        try:
            from moviepy import AudioFileClip
            clip = AudioFileClip(output_path)
            duration = clip.duration
            clip.close()
        except ImportError:
            print("MoviePy not found for duration calc, returning 0")
        
        return output_path, duration
