import subprocess
import os
import shutil

class VideoPostProcessor:
    def __init__(self):
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Simple check to ensure ffmpeg is installed and callable."""
        if shutil.which("ffmpeg") is None:
            raise EnvironmentError("ffmpeg is not installed or not found in system PATH.")

    def combine_video_audio(self, video_path: str, audio_path: str, output_path: str):
        """
        Merges video and audio.
        - map 0:v (video from first input)
        - map 1:a (audio from second input)
        - shortest: finish when the shortest stream ends (usually audio matches video now)
        - y: overwrite output
        """
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",        # Copy video stream (no re-encode if possible)
            "-c:a", "aac",         # Encode audio to aac
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",           # End when the shortest stream ends
            output_path
        ]
        
        print(f"Running ffmpeg merge: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"FFmpeg failed to create {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg merge failed: {e.stderr.decode()}")
            raise e

    def add_text_overlay(self, video_path: str, text: str, output_path: str):
        """
        Adds a text overlay to the video.
        - drawtext filter
        """
        # Sanitize text for ffmpeg (basic)
        sanitized_text = text.replace(":", "\:").replace("'", "")
        
        # Filter: White text, bottom center, with a semi-transparent black box background
        # fontfile is optional but recommended. Using default sans-serif if not specified.
        # box=1: enable box, boxcolor: black with 0.5 alpha
        filter_str = (
            f"drawtext=text='{sanitized_text}':"
            "fontcolor=white:fontsize=48:"
            "box=1:boxcolor=black@0.5:boxborderw=5:"
            "x=(w-text_w)/2:y=h-th-50" 
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", filter_str,
            "-an", # Mute audio from the source
            output_path
        ]

        print(f"Running ffmpeg overlay: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg overlay failed: {e.stderr.decode()}")
            raise e

    def get_duration(self, file_path: str) -> float:
        """Returns duration in seconds using ffprobe."""
        cmd = [
            "ffprobe", 
            "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            file_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    def concatenate_videos(self, video_paths: list, output_path: str):
        """
        Concatenates multiple video files into one using ffmpeg concat demuxer.
        """
        if not video_paths:
            return None
            
        list_file = "concat_list.txt"
        try:
            # Create the list file
            with open(list_file, "w") as f:
                for path in video_paths:
                    # FFmpeg requires absolute paths or relative safe paths. 
                    # Escaping is important.
                    # We'll use absolute paths for safety.
                    abs_path = os.path.abspath(path).replace("\\", "/")
                    f.write(f"file '{abs_path}'\n")
            
            cmd = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", list_file,
                "-c", "copy",
                output_path
            ]
            
            print(f"Running ffmpeg concat: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg concat failed: {e.stderr.decode()}")
            raise e
        finally:
            if os.path.exists(list_file):
                os.remove(list_file)

    def concatenate_with_transitions(self, video_paths: list, output_path: str, transition_duration: float = 0.5):
        """
        Concatenates videos with cross-fade transitions using FFmpeg xfade/acrossfade.
        """
        if not video_paths:
            return None
            
        if len(video_paths) == 1:
            # Just copy the single file
            try:
                shutil.copy(video_paths[0], output_path)
                return output_path
            except Exception as e:
                print(f"Error copying single video: {e}")
                raise e

        # 1. Get durations for xfade offsets
        durations = []
        for path in video_paths:
            d = self.get_duration(path)
            if d == 0:
                print(f"Warning: Could not get duration for {path}, assuming 4.0s default")
                d = 4.0
            durations.append(d)

        # 2. Build Filter Complex
        # Inputs
        input_args = []
        for path in video_paths:
            input_args.extend(["-i", path])

        filter_complex = ""
        
        # --- Video Chain (xfade) ---
        # Logic: [0:v][1:v]xfade=...[v1]; [v1][2:v]xfade=...[v2]...
        # Offset calculation is cumulative absolute time of the specific cut point.
        
        current_offset = durations[0] - transition_duration
        
        # Initialize loop
        # First transition: 0 and 1 -> v1
        filter_complex += f"[0:v][1:v]xfade=transition=fade:duration={transition_duration}:offset={current_offset}[v1];"
        
        last_v_label = "[v1]"
        
        # Subsequent transitions
        for i in range(2, len(video_paths)):
            # Update offset for the NEXT joint
            # The previous clip (input i-1) contributed (duration[i-1] - transition) to the timeline
            current_offset += (durations[i-1] - transition_duration)
            
            output_label = f"[v{i}]"
            filter_complex += f"{last_v_label}[{i}:v]xfade=transition=fade:duration={transition_duration}:offset={current_offset}{output_label};"
            last_v_label = output_label

        # --- Audio Chain (acrossfade) ---
        # Logic: [0:a][1:a]acrossfade=d=...[a1]; [a1][2:a]acrossfade=d=...[a2]...
        
        filter_complex += f"[0:a][1:a]acrossfade=d={transition_duration}[a1];"
        last_a_label = "[a1]"
        
        for i in range(2, len(video_paths)):
            output_label = f"[a{i}]"
            filter_complex += f"{last_a_label}[{i}:a]acrossfade=d={transition_duration}{output_label};"
            last_a_label = output_label

        # Remove trailing semicolon if strictly needed (ffmpeg usually tolerates it)
        filter_complex = filter_complex.strip(";")

        cmd = [
            "ffmpeg",
            "-y"
        ]
        cmd.extend(input_args)
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", last_v_label,
            "-map", last_a_label,
            "-c:v", "libx264",    # Must re-encode for filters
            "-c:a", "aac",        # Must re-encode for filters
            # Optimization: ultrafast for MVP speed, crf 23 for default quality
            "-preset", "ultrafast", 
            output_path
        ])

        print(f"Running ffmpeg xfade: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg xfade failed: {e.stderr.decode()}")
            raise e
