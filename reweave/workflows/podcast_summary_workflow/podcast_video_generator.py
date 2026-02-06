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
from typing import Dict, Optional

import yt_dlp
from dotenv import load_dotenv
from moviepy import AudioFileClip, ColorClip, TextClip, CompositeVideoClip, vfx
from youtube_transcript_api import YouTubeTranscriptApi

from reweave.ai.gemini_service import generate_text, generate_audio
from reweave.utils.video_utils import DEFAULT_FONT


class PodcastVideoGenerator:
    def __init__(self, assemblyai_api_key: Optional[str] = None):
        load_dotenv()
        self.assemblyai_api_key = assemblyai_api_key or os.getenv(
            "ASSEMBLYAI_API_KEY")

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
        }

    def transcribe_youtube_native(self, youtube_url: str, languages=None) -> str:
        """
        Fetch transcript directly from YouTube using youtube-transcript-api.
        """
        if languages is None:
            languages = ['en']
        video_id = youtube_url.split('v=')[-1].split('&')[0]
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=languages)
        return '\n'.join(item.text for item in transcript)

    def summarize_text(self, text: str) -> str:
        response = generate_text(
            system_prompt="Summarize into concise bullet points without losing important details. The transcription might contain mixed languages Hindi and English. Interpret the context and summarize accordingly.",
            user_prompt=text,
            temperature=0.5,
        )
        return response.content or ""

    def synthesize_speech(self, text: str, out_path: str) -> str:
        if os.path.exists(out_path):
            os.remove(out_path)
        audio = generate_audio(text)
        audio.stream_to_file(out_path)
        return out_path

    def create_scrolling_video(self, summary: str, audio_path: str, video_path: str) -> str:
        s = self.video_settings
        clip_audio = AudioFileClip(audio_path)
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
        video = CompositeVideoClip([bg, mov]).with_effects([
            vfx.MultiplySpeed(factor=s['speedup_factor'])
        ])
        audio_clip = clip_audio.with_start(s['delay']/s['speedup_factor'])
        final = video.with_audio(audio_clip)
        if os.path.exists(video_path):
            os.remove(video_path)
        final.write_videofile(video_path, fps=s['fps'], codec='libx264',
                              audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)
        return video_path

    def generate_video_from_url(self, youtube_url: str, output_dir: str = 'output') -> Dict[str, object]:
        os.makedirs(output_dir, exist_ok=True)
        meta = self.get_youtube_metadata(youtube_url)
        transcript = self.transcribe_youtube_native(youtube_url)
        summary = self.summarize_text(transcript)
        audio_path = os.path.join(output_dir, 'summary.mp3')
        self.synthesize_speech(summary, audio_path)
        video_path = os.path.join(output_dir, 'summary_video.mp4')
        self.create_scrolling_video(summary, audio_path, video_path)
        txt_t = os.path.join(output_dir, 'transcript.txt')
        txt_s = os.path.join(output_dir, 'summary.txt')
        with open(txt_t, 'w') as f:
            f.write(transcript)
        with open(txt_s, 'w') as f:
            f.write(summary)
        return {'video': video_path, 'audio': audio_path, 'transcript': txt_t, 'summary': txt_s, 'metadata': meta}
