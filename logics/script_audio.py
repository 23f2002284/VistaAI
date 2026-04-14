import json
import wave
import os
from google import genai
from google.genai import types
from logics.config import GEMINI_API_KEY
from logics.prompts import SCRIPT_AUDIO_PROMPT, MASTER_SCRIPT_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)

class ScriptGenerator:
    @staticmethod
    def generate_script(property_description: str, script: str, preference: str) -> dict:
        prompt = SCRIPT_AUDIO_PROMPT.format(
            property_description=property_description,
            preference=preference,
            script=script
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def generate_master_script(images_bytes: list, address: str, rough_notes: str, preference: str) -> dict:
        prompt_text = (
            f"You are a real estate marketing copywriter preparing a simple, relaxed cinematic video. "
            f"I have provided {len(images_bytes)} images of a property located at '{address}'. "
            f"The desired aesthetic is '{preference}'. The user notes: '{rough_notes}'.\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Write a very simple, easy-to-understand, slow-paced voice-over script.\n"
            f"2. Write EXACTLY {len(images_bytes)} sentences. Sentence 1 MUST introduce the address '{address}'. The FINAL sentence MUST be a strong Call-to-Action outro (e.g., 'Contact us today to know more!', 'Visit today!', or 'Grab this offer now!').\n"
            f"3. Keep each sentence extremely brief. Do not exceed 10 words per sentence.\n"
            f"4. Provide exactly {len(images_bytes)} highly descriptive 1-3 word overlay keywords corresponding to each image (e.g., 'Modern Kitchen', 'Spacious Living').\n"
            f"Return ONLY valid JSON matching this schema exactly:\n"
            '{"script": "Complete continuous script here...", "keywords": ["Keyword1", "Keyword2"]}'
        )
        
        contents = [prompt_text]
        for img_bytes in images_bytes:
            contents.append(
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            )
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        import json
        try:
            return json.loads(response.text)
        except Exception:
            return {"script": response.text, "keywords": ["Stunning View"] * len(images_bytes)}

    @staticmethod
    def generate_audio(input_data: str, voice_name: str = "kore", output_prefix: str = "scene") -> list:
        import subprocess
        
        # UI mapping to pristine Edge-TTS neural characters
        voice_map = {
            "kore": "en-US-AriaNeural",
            "puck": "en-GB-RyanNeural",
            "aoede": "en-US-JennyNeural"
        }
        edge_voice = voice_map.get(voice_name.lower(), "en-US-AriaNeural")
        
        output_path = f"uploads/{output_prefix}_audio.mp3"
        # Force a slightly slower, relaxed narration pace
        cmd = ["edge-tts", "--text", input_data, "--voice", edge_voice, "--rate=-15%", "--write-media", output_path]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return [output_path]
        except Exception as e:
            print(f"Edge-TTS synthesis failed safely: {e}. Falling back to 4s silence track.")
            import wave
            fallback_path = f"uploads/{output_prefix}_audio.wav"
            with wave.open(fallback_path, "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(24000)
                # 4s silence at 24000Hz 16-bit Mono
                w.writeframes(b'\x00' * (24000 * 2 * 4))
            return [fallback_path]
