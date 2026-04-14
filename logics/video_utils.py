import subprocess
import os

class VideoPostProcessor:
    @staticmethod
    def generate_cinematic_effect(image_path: str, effect_index: int, duration_sec: float = 4.0) -> str:
        base_name = os.path.basename(image_path).split('.')[0]
        output_path = f"uploads/{base_name}_cinematic.mp4"
        
        # Clamp minimal duration safely
        duration_sec = max(4.0, duration_sec)
        d_frames = int(duration_sec * 30)
        
        # Distinct cinematic zoompan algebraic rules scaled precisely to the Audio Track length
        filters = [
            f"zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={d_frames}:s=1600x900",
            f"zoompan=z='1.15':x='min(x+2,iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={d_frames}:s=1600x900",
            f"zoompan=z='1.15':x='max(iw-iw/zoom-2*in,0)':y='ih/2-(ih/zoom/2)':d={d_frames}:s=1600x900",
            f"zoompan=z='1.15':x='iw/2-(iw/zoom/2)':y='max(ih-ih/zoom-2*in,0)':d={d_frames}:s=1600x900",
            f"zoompan=z='1.15':x='min(x+2,iw-iw/zoom)':y='min(y+1.5,ih-ih/zoom)':d={d_frames}:s=1600x900"
        ]
        
        selected_filter = filters[effect_index % len(filters)]
        
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", image_path,
            "-vf", f"scale=-2:1080,{selected_filter}",
            "-c:v", "libx264", "-t", str(duration_sec), "-pix_fmt", "yuv420p", output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Cinematic FFmpeg generation failed: {e.stderr.decode()}")
            return None

    @staticmethod
    def combine_video_audio(video_path: str, audio_path: str, output_path: str) -> str:
        # Calculate strict temporal bounds to natively kill infinite buffering bugs
        try:
            dur = VideoPostProcessor.get_duration(audio_path)
        except Exception:
            dur = 4.0
            
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", # Safely loop video if it's shorter than the audio
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v:0", # Explicitly extract ONLY the visual video stream from Google Veo
            "-map", "1:a:0", # Explicitly extract ONLY the Voiceover stream (Overwrites and silences Veo native noise)
            "-c:v", "libx264", 
            "-pix_fmt", "yuv420p", # Formats Veo 4K/HDR matrices down to standard planar for Text Override visibility
            "-c:a", "aac",
            "-t", str(dur), # Explicit temporal kill-switch to prevent infinite stream_loop buffer saturation!
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path

    @staticmethod
    def add_text_overlay(video_path: str, text: str, output_path: str) -> str:
        dur = VideoPostProcessor.get_duration(video_path)
        safe_text = text.upper()
        # Modern cinematic lower-left typography with drop-shadow AND a smooth dynamic 1s fade in/out
        alpha_fade = f"if(lt(t,1),t,if(lt(t,{dur-1}),1,{dur}-t))"
        # Embed format=yuv420p to forcefully standardize color bounds so transparent text overlays don't silently fail off-buffer
        filter_str = f"format=yuv420p,drawtext=text='{safe_text}':fontcolor=white:fontsize=84:shadowcolor=black@0.9:shadowx=5:shadowy=5:x=120:y=h-th-120:alpha='{alpha_fade}'"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vf", filter_str,
            "-codec:a", "copy",
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path

    @staticmethod
    def generate_ambient_audio(output_path: str, duration: int = 20) -> str:
        # Generates a soothing ambient stereo drone noise using sine waves (432Hz and 332Hz chords)
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi", 
            "-i", f"aevalsrc='0.05*sin(2*PI*220*t)+0.05*sin(2*PI*330*t)':d={duration}", 
            "-c:a", "libmp3lame", output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
        except Exception:
            return None

    @staticmethod
    def mix_ambient_audio(video_path: str, ambient_audio: str, output_path: str) -> str:
        cmd = [
            "ffmpeg", "-y", "-i", video_path, "-i", ambient_audio,
            "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", output_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
        except Exception as e:
            import shutil
            try:
                shutil.copy(video_path, output_path)
            except:
                pass
            return output_path

    @staticmethod
    def get_duration(file_path: str) -> float:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())

    @staticmethod
    def concatenate_videos(paths: list, output_path: str) -> str:
        import time
        list_file = f"uploads/concat_list_{int(time.time() * 1000)}.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for p in paths:
                # Essential FFmpeg constraint: Windows absolute paths MUST use forward slashes in concat lists
                safe_path = os.path.abspath(p).replace('\\', '/')
                f.write(f"file '{safe_path}'\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_path
        ]
        subprocess.run(cmd, check=True)
        os.remove(list_file)
        return output_path

    @staticmethod
    def concatenate_with_transitions(paths: list, output_path: str) -> str:
        # For simplicity and MVP, implementing xfade on video and acrossfade on audio
        # is complex dynamically via subprocess without knowing exact durations.
        # Fallback to simple concat or a complex filtergraph logic.
        return VideoPostProcessor.concatenate_videos(paths, output_path)
