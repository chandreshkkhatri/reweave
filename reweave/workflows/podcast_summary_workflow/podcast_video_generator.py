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
    transcribe_youtube_url, transcribe_youtube_url_chunked
)
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
        ydl_opts = {'quiet': True}
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
        return out_path

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

    def generate_video_from_url(self, youtube_url: str, output_dir: str = 'output',
                                use_audio_transcription: bool = True) -> Dict[str, object]:
        os.makedirs(output_dir, exist_ok=True)
        meta = self.get_youtube_metadata(youtube_url)

        # Try Gemini native YouTube transcription (new, experimental)
        # Falls back to audio-based or YouTube native captions on failure
        if use_audio_transcription:
            try:
                print(f"Attempting Gemini native transcription for: {youtube_url}")
                duration = meta.get('duration')
                if duration and duration > 600: # If longer than 10 minutes, use chunked
                    print(f"Video duration ({duration}s) exceeds threshold. Using chunked transcription.")
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
        video_path = os.path.join(output_dir, 'summary_video.mp4')
        title = meta.get('title', '')
        self.create_scrolling_video(summary, audio_path, video_path, title)
        txt_t = os.path.join(output_dir, 'transcript.txt')
        txt_s = os.path.join(output_dir, 'summary.txt')
        with open(txt_t, 'w') as f:
            f.write(transcript)
        with open(txt_s, 'w') as f:
            f.write(summary)
        return {'video': video_path, 'audio': audio_path, 'transcript': txt_t, 'summary': txt_s, 'metadata': meta}
