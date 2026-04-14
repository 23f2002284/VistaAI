from google import genai
from google.genai import types
from PIL import Image
from logics.config import GEMINI_API_KEY
from logics.prompts import SCRIPT_AUDIO_PROMPT
import wave
import json

class ScriptGenerator:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            print("Gemini Setup Complete")
        except Exception as e:
            print(f"Warning: Gemini Init Failed: {e}")
            self.client = None
    
    def _clean_json_response(self, text_response: str) -> str:
        if text_response.startswith("```"):
            return text_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return text_response

    def generate_script(
        self, 
        property_description: str, 
        script: str = "",
        preference: str = "Standard real estate marketing", 
    ) -> dict:
        try:
            prompt = SCRIPT_AUDIO_PROMPT.format(
                property_description=property_description,
                script=script, 
                preference=preference
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            clean_text = self._clean_json_response(response.text)
            return json.loads(clean_text)
        except Exception as e:
            print(f"Error generating script: {e}")
            raise e
            
    def generate_master_script(
        self,
        room_sequence: list,
        rough_notes: str = "",
        preference: str = "Standard real estate marketing"
    ) -> dict:
        try:
            from logics.prompts import MASTER_SCRIPT_PROMPT
            
            prompt = MASTER_SCRIPT_PROMPT.format(
                room_sequence=", ".join(room_sequence),
                rough_notes=rough_notes,
                preference=preference
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            clean_text = self._clean_json_response(response.text)
            return json.loads(clean_text)
        except Exception as e:
            print(f"Error generating master script: {e}")
            raise e

    def wave_file(self, filename, pcm, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm)

    def generate_audio(self, input_data, voice_name: str = "Kore", output_prefix: str = "scene") -> list:
        """
        Generates audio from input (text or dict plan) and returns list of filenames.
        Enforces 4s duration.
        """
        generated_files = []
        
        # Determine items to process
        items = []
        if isinstance(input_data, dict) and "tour_plan" in input_data:
            for scene in input_data["tour_plan"]:
                items.append({
                    "text": scene.get("narration_text", ""),
                    "filename": f"{output_prefix}_{scene.get('sequence_id', 'unknown')}.wav"
                })
        elif isinstance(input_data, str):
            items.append({
                "text": input_data,
                "filename": f"{output_prefix}.wav"
            })
        else:
            print("Invalid input format for generate_audio")
            return []

        TARGET_DURATION = 4.0  # seconds
        SAMPLE_RATE = 24000
        SAMPLE_WIDTH = 2  # 16-bit
        TARGET_SIZE = int(TARGET_DURATION * SAMPLE_RATE * SAMPLE_WIDTH)

        for item in items:
            try:
                text = item["text"]
                filename = item["filename"]
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-preview-tts",
                    contents=text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_name,
                                )
                            )
                        ),
                    )
                )
                
                # Extract raw PCM data
                if not response.candidates:
                     print(f"No audio candidate for {text}")
                     continue
                     
                raw_audio = response.candidates[0].content.parts[0].inline_data.data
                
                # Process audio duration
                current_size = len(raw_audio)
                
                if current_size < TARGET_SIZE:
                    # Pad with silence (zeros)
                    padding = b'\x00' * (TARGET_SIZE - current_size)
                    final_audio = raw_audio + padding
                else:
                    # Trim to fit
                    final_audio = raw_audio[:TARGET_SIZE]
                
                self.wave_file(filename, final_audio, rate=SAMPLE_RATE)
                generated_files.append(filename)
                
            except Exception as e:
                print(f"Error generating audio for {item.get('filename')}: {e}")
                
        return generated_files