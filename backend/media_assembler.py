from moviepy import VideoFileClip, AudioFileClip, vfx

class MediaAssembler:
    def assemble_final_video(self, video_path: str, audio_path: str, output_path: str = "final_output.mp4") -> str:
        """
        Combines the video transition and the generated audio.
        Stretches (slows down/speeds up) the video to match the audio duration exactly.
        """
        try:
            # Load clips
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            video_duration = video_clip.duration
            audio_duration = audio_clip.duration
            
            print(f"Video Duration: {video_duration}s, Audio Duration: {audio_duration}s")
            
            # Key Feature: Sync Logic
            # "Generated video length and audio length should be of same length to not make issue in syncronization"
            # We assume user prefers Audio to dictate length (narration).
            # So we stretch video to match audio.
            
            # Calculate speed factor
            # new_duration = original / speed_factor => speed_factor = original / new
            speed_factor = video_duration / audio_duration
            
            # Apply speed effect to match duration
            # Note: speedx is the standard fx in MoviePy
            final_video = video_clip.with_effects([vfx.MultiplySpeed(speed_factor)]) \
                         if hasattr(vfx, "MultiplySpeed") else video_clip.fx(vfx.speedx, factor=speed_factor)
            
            # Ideally use set_duration? No, that just cuts or loops. We need retiming.
            # Safe way in newer moviepy might vary, but speedx usually works if audio is set after.
            
            # Ensure precise set
            final_video = final_video.with_audio(audio_clip)
            final_video = final_video.with_duration(audio_duration)
            
            # Export
            # Using defaults for libx264
            print(f"Exporting final video to {output_path}...")
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            
            # Cleanup
            video_clip.close()
            audio_clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error assembling video: {e}")
            raise e
