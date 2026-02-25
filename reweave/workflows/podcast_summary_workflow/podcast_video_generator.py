"""
Podcast Video Generator

Core logic for transcription, summary, TTS, and video creation.

Dependencies:
    yt-dlp
    python-dotenv
    google-genai
    gtts
    moviepy
    youtube-transcript-api

Environment Variables:
    GEMINI_API_KEY
"""
import os
from typing import Dict
from urllib.parse import urlparse, parse_qs

import yt_dlp
from dotenv import load_dotenv
from moviepy import (
    AudioFileClip, ColorClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, vfx,
)
from youtube_transcript_api import YouTubeTranscriptApi

from reweave.ai.gemini_service import (
    generate_text, generate_audio, transcribe_audio,
    transcribe_youtube_url, transcribe_youtube_url_chunked,
    generate_image, get_youtube_metadata_gemini,
    generate_subtitles, get_visual_keywords
)
from reweave.ai.fal_service import generate_live_portrait as generate_live_portrait_fal
from reweave.ai.replicate_service import generate_live_portrait_replicate
from reweave.utils.video_utils import DEFAULT_FONT, create_title_card


class PodcastVideoGenerator:
    def __init__(self):
        load_dotenv()

        # Video settings
        self.video_settings = {
            'width': 1280,
            'height': 720,
            'fps': 24,
            'font_size': 30,
            'text_color': 'white',
            'bg_color': (0, 0, 0),
            'text_width': 1000,
            'delay': 8,
            'tail': 8,
            'speed_factor': 0.85,
            'speedup_factor': 1.15
        }

    def get_youtube_metadata(self, youtube_url: str) -> Dict:
        """Get metadata preferring Gemini native extraction to avoid yt-dlp bot detection."""
        try:
            print(f"Extracting metadata for {youtube_url} using Gemini...")
            return get_youtube_metadata_gemini(youtube_url)
        except Exception as e:
            print(f"Gemini metadata extraction failed: {e}. Falling back to yt-dlp...")
            
        ydl_opts = {'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
            if not info:
                raise ValueError("Failed to extract YouTube metadata")
            return {
                'title': info.get('title'),
                'description': info.get('description'),
                'uploader': info.get('uploader'),
                'tags': info.get('tags'),
                'duration': info.get('duration'),
            }
        except Exception as e:
            print(f"Warning: yt-dlp metadata extraction failed: {e}. Using fallback info.")
            # Basic fallback if yt-dlp fails (common in server environments)
            return {
                'title': 'YouTube Video',
                'description': '',
                'uploader': 'Unknown',
                'duration': 600, # Default to 10 mins to avoid immediate chunking if unknown
            }

    def transcribe_youtube_native(self, youtube_url: str, languages=None) -> str:
        """
        Fetch transcript directly from YouTube using youtube-transcript-api.
        """
        if languages is None:
            languages = ['en']
        parsed = urlparse(youtube_url)
        if parsed.hostname in ('youtu.be',):
            video_id = parsed.path.lstrip('/')
        else:
            video_id = parse_qs(parsed.query).get('v', [''])[0]
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=languages)
        return '\n'.join(item.text for item in transcript)

    def download_youtube_audio(self, youtube_url: str, output_dir: str) -> str:
        """Download audio from a YouTube video using yt-dlp."""
        audio_path = os.path.join(output_dir, 'source_audio')
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return audio_path + '.mp3'

    def transcribe_from_audio(self, audio_path: str) -> str:
        """Transcribe a local audio file using Gemini's audio understanding."""
        return transcribe_audio(audio_path)

    def summarize_text(self, text: str) -> str:
        response = generate_text(
            system_prompt=(
                "You are an expert content summarizer. Create a clear, well-structured "
                "summary of the following transcript.\n\n"
                "Guidelines:\n"
                "- Start with a one-line overview of what the content is about.\n"
                "- Use concise bullet points grouped by topic or theme.\n"
                "- Preserve key facts, names, numbers, and specific claims.\n"
                "- Capture the speaker's main arguments and conclusions.\n"
                "- If the transcript contains mixed languages (e.g. Hindi and English), "
                "interpret the full context and summarize in English.\n"
                "- Omit filler words, repetitions, and off-topic tangents.\n"
                "- Aim for a summary that is roughly 15-20% the length of the original."
            ),
            user_prompt=text,
            temperature=0.3,
        )
        return response.content or ""

    def synthesize_speech(self, text: str, out_path: str) -> str:
        if os.path.exists(out_path):
            os.remove(out_path)
        audio = generate_audio(text)
        audio.stream_to_file(out_path)
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of an audio file in seconds."""
        from moviepy import AudioFileClip
        clip = AudioFileClip(audio_path)
        duration = clip.duration
        clip.close()
        return duration

    def generate_speaker_image(self, transcript: str, output_path: str, speaker_description: str = None) -> str:
        """Generate a portrait of the speaker based on the transcript and optional description."""
        # Use Gemini to generate a descriptive prompt for the speaker
        system_msg = "Based on the following transcript, describe what the main speaker looks like. Create a descriptive prompt for an AI image generator to create a high-quality, professional portrait of them. Focus on facial features, age, gender, and professional appearance. Output ONLY the image generation prompt."
        if speaker_description:
            system_msg += f" IMPORTANT: The speaker should be {speaker_description}."
            
        prompt_resp = generate_text(
            system_prompt=system_msg,
            user_prompt=transcript[:5000], # Use first 5k chars for context
            temperature=0.4
        )
        image_prompt = prompt_resp.content or "A professional portrait of a tech podcast host."
        print(f"Generating speaker image with prompt: {image_prompt}")
        
        image_bytes = generate_image(image_prompt)
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        return output_path

    def create_liveportrait_video(self, portrait_image_path: str, audio_path: str, video_path: str, driving_video_url: str = None) -> str:
        """Synthesize a talking-head video using LivePortrait (fal.ai or Replicate)."""
        replicate_token = os.getenv("REPLICATE_API_TOKEN")
        fal_key = os.getenv("FAL_KEY")
        
        if driving_video_url is None:
            # Default driving video
            driving_video_url = "https://storage.googleapis.com/falserverless/model_tests/live-portrait/liveportrait-example.mp4"
            
        try:
            if fal_key:
                print("FAL_KEY found. Using fal.ai for Talking Head (EchoMimic)...")
                from reweave.ai.fal_service import generate_live_portrait as generate_live_portrait_fal
                # Use the actual summary audio for lip-syncing
                result_url = generate_live_portrait_fal(portrait_image_path, audio_path=audio_path)
            elif replicate_token:
                print("REPLICATE_API_TOKEN found. Using Replicate for Talking Head (SadTalker)...")
                # Use the actual summary audio for lip-syncing
                result_url = generate_live_portrait_replicate(portrait_image_path, audio_path)
            else:
                raise ValueError("Neither REPLICATE_API_TOKEN nor FAL_KEY found. Cannot generate LivePortrait.")

            print(f"LivePortrait generated at: {result_url}")
            
            # Download the result to the local video_path
            import requests
            resp = requests.get(result_url)
            with open(video_path, "wb") as f:
                f.write(resp.content)
            
            print(f"LivePortrait video saved to {video_path}")
            return video_path
            
        except Exception as e:
            print(f"LivePortrait synthesis failed: {e}. Ensure you have credits and correct API keys.")
            raise e

    def create_scrolling_video(self, summary: str, audio_path: str, video_path: str,
                               title: str = '') -> str:
        s = self.video_settings
        clip_audio = AudioFileClip(audio_path)
        try:
            duration = clip_audio.duration
            total = (s['delay'] + duration + s['tail']) * s['speed_factor']
            bg = ColorClip((s['width'], s['height']),
                           color=s['bg_color'], duration=total)
            txt = TextClip(
                font=DEFAULT_FONT,
                text=summary,
                font_size=s['font_size'],
                color=s['text_color'],
                size=(s['text_width'], None),
                method='caption',
            )
            h, w = txt.h, txt.w
            x0 = (s['width'] - w) // 2
            def pos(t): return (x0, s['height'] - (s['height'] + h) * (t/total))
            mov = txt.with_position(pos).with_duration(total)
            scroll_video = CompositeVideoClip([bg, mov]).with_effects([
                vfx.MultiplySpeed(factor=s['speedup_factor'])
            ])
            audio_clip = clip_audio.with_start(s['delay']/s['speedup_factor'])
            scroll_with_audio = scroll_video.with_audio(audio_clip)

            # Prepend title card if title is available
            clips = []
            if title:
                title_card = create_title_card(
                    title, duration=3,
                    width=s['width'], height=s['height'],
                    font_size=40,
                )
                clips.append(title_card)
            clips.append(scroll_with_audio)

            final = concatenate_videoclips(clips)
            final.write_videofile(video_path, fps=s['fps'], codec='libx264',
                                  audio_codec='aac',
                                  temp_audiofile=f'temp-summary-audio-{os.getpid()}.m4a',
                                  remove_temp=True)
        finally:
            clip_audio.close()
        return video_path

    def create_slideshow_video(self, summary: str, audio_path: str, video_path: str, output_dir: str) -> str:
        """Create a slideshow video with Ken Burns effects and burned-in captions."""
        import subprocess
        from moviepy import AudioFileClip
        
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        audio_clip.close()
        
        # 1. Generate subtitles
        srt_path = os.path.join(output_dir, 'summary.srt')
        srt_content = generate_subtitles(summary, duration)
        with open(srt_path, 'w') as f:
            f.write(srt_content)
            
        # 2. Get visual keywords and generate images
        keywords = get_visual_keywords(summary, num_keywords=4)
        image_paths = []
        for i, kw in enumerate(keywords):
            img_path = os.path.join(output_dir, f'slideshow_{i}.png')
            img_prompt = f"A professional, cinematic illustration representing {kw}. Minimalist and high-quality."
            img_bytes = generate_image(img_prompt)
            with open(img_path, 'wb') as f:
                f.write(img_bytes)
            image_paths.append(img_path)
            
        # 3. Create a complex FFmpeg filter to stitch them with Ken Burns and transitions
        # This is a simplified version: one image for the whole duration with Ken Burns
        # A more complex one would swap images. Let's do a sequence of images.
        num_images = len(image_paths)
        seg_dur = duration / num_images
        
        # For each image, create a 720p segment with zoompan
        input_args = []
        filter_complex = []
        for i, img in enumerate(image_paths):
            input_args.extend(['-loop', '1', '-t', str(seg_dur), '-i', img])
            # Zoompan filter for Ken Burns effect
            filter_complex.append(f"[{i}:v]scale=1280:720,zoompan=z='min(zoom+0.001,1.5)':d={int(seg_dur*24)}:s=1280x720[v{i}];")
            
        # Concatenate visuals
        concat_input = "".join([f"[v{i}]" for i in range(num_images)])
        filter_complex.append(f"{concat_input}concat=n={num_images}:v=1:a=0[vfinal];")
        
        # Burn in subtitles (FFmpeg subtitles filter needs special escaping for paths)
        # We'll use a local relative path if possible, or escape properly
        safe_srt_path = srt_path.replace(":", "\\:").replace("\\", "/")
        filter_complex.append(f"[vfinal]subtitles='{safe_srt_path}':force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Alignment=2'[vcap]")

        cmd = [
            'ffmpeg', '-y'
        ] + input_args + [
            '-i', audio_path,
            '-filter_complex', "".join(filter_complex),
            '-map', '[vcap]',
            '-map', f'{num_images}:a', # The audio input is the last one
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-shortest',
            video_path
        ]
        
        print(f"Running FFmpeg for slideshow: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return video_path

    def create_audiogram_video(self, summary: str, background_image_path: str, audio_path: str, video_path: str, output_dir: str) -> str:
        """Create an audiogram with reactive waveform and burned-in captions."""
        import subprocess
        from moviepy import AudioFileClip
        
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        audio_clip.close()
        
        srt_path = os.path.join(output_dir, 'summary.srt')
        srt_content = generate_subtitles(summary, duration)
        with open(srt_path, 'w') as f:
            f.write(srt_content)

        safe_srt_path = srt_path.replace(":", "\\:").replace("\\", "/")
        
        # FFmpeg filter:
        # 1. Scale background to 720p and split for multiple uses
        # 2. Crop and blur the middle region (waveform) and bottom region (subtitles)
        # 3. Add showwaves filter for audio waveform, center vertically
        # 4. Burn in subtitles
        filter_complex = (
            "[0:v]scale=1280:720,split=3[bg][bg_c1][bg_c2];"
            "[bg_c1]crop=1280:200:0:260,boxblur=20:5[blur_wave];"
            "[bg_c2]crop=1280:150:0:570,boxblur=20:5[blur_sub];"
            "[bg][blur_wave]overlay=0:260[bg1];"
            "[bg1][blur_sub]overlay=0:570[bg2];"
            "[1:a]showwaves=s=1280x200:mode=cline:colors=white:r=24[wave];"
            "[bg2][wave]overlay=0:(H-h)/2[vwave];"
            f"[vwave]subtitles='{safe_srt_path}':force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Alignment=2'[vfinal]"
        )
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-t', str(duration), '-i', background_image_path,
            '-i', audio_path,
            '-filter_complex', filter_complex,
            '-map', '[vfinal]',
            '-map', '1:a',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-shortest',
            video_path
        ]
        
        print(f"Running FFmpeg for audiogram: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return video_path

    def extract_frames_from_youtube(self, youtube_url: str, timestamps: list, output_dir: str) -> list:
        """Extract specific frames from a YouTube video without downloading the whole thing."""
        import subprocess
        os.makedirs(output_dir, exist_ok=True)
        
        # Get stream URL
        cmd_url = [os.path.join(os.getcwd(), '.venv/bin/yt-dlp'), '-g', '-f', 'bestvideo[height<=720]', youtube_url]
        try:
            stream_url = subprocess.check_output(cmd_url, text=True).strip()
        except Exception as e:
            print(f"Failed to get stream URL: {e}. Falling back to slower method...")
            # Fallback to python-based if needed, but let's assume .venv works
            return []

        frame_paths = []
        for i, ts in enumerate(timestamps):
            out_path = os.path.join(output_dir, f'screenshot_{i}.png')
            # Extract one frame at timestamp ts
            cmd_f = [
                'ffmpeg', '-y', 
                '-ss', str(ts), 
                '-i', stream_url, 
                '-vframes', '1', 
                '-q:v', '2',
                out_path
            ]
            print(f"Extracting frame at {ts}s to {out_path}...")
            subprocess.run(cmd_f, check=False) # check=False to skip occasional seeking errors
            if os.path.exists(out_path):
                frame_paths.append(out_path)
        return frame_paths

    def create_screenshot_slideshow_video(self, summary: str, youtube_url: str, duration: float, audio_path: str, video_path: str, output_dir: str) -> str:
        """Create a slideshow using actual screenshots from the podcast video."""
        # 1. Subtitles
        srt_path = os.path.join(output_dir, 'summary.srt')
        srt_content = generate_subtitles(summary, duration)
        with open(srt_path, 'w') as f:
            f.write(srt_content)
            
        # 2. Extract 5-10 screenshots evenly spaced
        num_frames = 6
        timestamps = [int(i * (duration / (num_frames + 1))) for i in range(1, num_frames + 1)]
        image_paths = self.extract_frames_from_youtube(youtube_url, timestamps, output_dir)
        
        if not image_paths:
            print("No screenshots extracted. Falling back to AI images...")
            return self.create_slideshow_video(summary, audio_path, video_path, output_dir)

        # 3. Create slideshow (reusing logic from create_slideshow_video but with existing images)
        import subprocess
        num_images = len(image_paths)
        seg_dur = duration / num_images
        
        input_args = []
        filter_complex = []
        for i, img in enumerate(image_paths):
            input_args.extend(['-loop', '1', '-t', str(seg_dur), '-i', img])
            filter_complex.append(f"[{i}:v]scale=1280:720,zoompan=z='min(zoom+0.001,1.5)':d={int(seg_dur*24)}:s=1280x720[v{i}];")
            
        concat_input = "".join([f"[v{i}]" for i in range(num_images)])
        filter_complex.append(f"{concat_input}concat=n={num_images}:v=1:a=0[vfinal];")
        
        safe_srt_path = srt_path.replace(":", "\\:").replace("\\", "/")
        filter_complex.append(f"[vfinal]subtitles='{safe_srt_path}':force_style='FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Alignment=2'[vcap]")

        cmd = [
            'ffmpeg', '-y'
        ] + input_args + [
            '-i', audio_path,
            '-filter_complex', "".join(filter_complex),
            '-map', '[vcap]',
            '-map', f'{num_images}:a',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-shortest',
            video_path
        ]
        
        print(f"Running FFmpeg for screenshot slideshow: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return video_path

    def generate_video_from_url(self, youtube_url: str, output_dir: str = 'output',
                                use_audio_transcription: bool = True,
                                speaker_description: str = None,
                                mode: str = 'auto') -> Dict[str, object]:
        """
        Generate summary video.
        Modes: 'avatar' (LivePortrait), 'slideshow' (Visual Summary), 'audiogram' (Waveform), 'scrolling', 'auto'
        """
        os.makedirs(output_dir, exist_ok=True)
        meta = self.get_youtube_metadata(youtube_url)

        # Transcription
        if use_audio_transcription:
            try:
                print(f"Attempting Gemini native transcription for: {youtube_url}")
                duration = meta.get('duration')
                if duration and duration > 600:
                    transcript = transcribe_youtube_url_chunked(youtube_url, duration)
                else:
                    transcript = transcribe_youtube_url(youtube_url)
            except Exception as e:
                print(f"Gemini native transcription failed: {e}. Falling back...")
                try:
                    source_audio = self.download_youtube_audio(youtube_url, output_dir)
                    transcript = self.transcribe_from_audio(source_audio)
                except Exception:
                    transcript = self.transcribe_youtube_native(youtube_url)
        else:
            transcript = self.transcribe_youtube_native(youtube_url)

        summary = self.summarize_text(transcript)
        audio_path = os.path.join(output_dir, 'summary.mp3')
        self.synthesize_speech(summary, audio_path)
        
        # Decide mode
        if mode == 'auto':
            if (os.getenv("FAL_KEY") is not None) or (os.getenv("REPLICATE_API_TOKEN") is not None):
                mode = 'avatar'
            else:
                mode = 'scrolling'
        
        print(f"Workflow mode set to: {mode}")
        video_path = os.path.join(output_dir, f'summary_video_{mode}.mp4')
        if mode == 'avatar':
            print("Generating Avatar (LivePortrait) summary video...")
            portrait_path = os.path.join(output_dir, 'speaker_portrait.png')
            self.generate_speaker_image(transcript, portrait_path, speaker_description=speaker_description)
            self.create_liveportrait_video(portrait_path, audio_path, video_path)
        elif mode == 'slideshow':
            print("Generating Visual Summary (Slideshow) video...")
            self.create_slideshow_video(summary, audio_path, video_path, output_dir)
        elif mode == 'screenshot_slideshow':
            print("Generating Screenshot Slideshow video...")
            duration_audio = self.get_audio_duration(audio_path)
            self.create_screenshot_slideshow_video(summary, youtube_url, duration_audio, audio_path, video_path, output_dir)
        elif mode == 'audiogram':
            print("Generating Dynamic Audiogram video...")
            portrait_path = os.path.join(output_dir, 'background.png')
            keywords = get_visual_keywords(summary, num_keywords=1)
            keyword = keywords[0] if keywords else "a professional podcast recording studio"
            img_prompt = f"A professional, cinematic illustration representing {keyword}. Minimalist, high-quality, suitable for a podcast background."
            img_bytes = generate_image(img_prompt)
            with open(portrait_path, 'wb') as f:
                f.write(img_bytes)
            self.create_audiogram_video(summary, portrait_path, audio_path, video_path, output_dir)
        else:
            print("Generating Scrolling Text summary video...")
            title = meta.get('title', '')
            self.create_scrolling_video(summary, audio_path, video_path, title)
            
        txt_t = os.path.join(output_dir, 'transcript.txt')
        txt_s = os.path.join(output_dir, 'summary.txt')
        with open(txt_t, 'w') as f:
            f.write(transcript)
        with open(txt_s, 'w') as f:
            f.write(summary)
        return {'video': video_path, 'audio': audio_path, 'transcript': txt_t, 'summary': txt_s, 'metadata': meta}
