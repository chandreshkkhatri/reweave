"""
Podcast Video Generator

Core logic extracted from notebook for transcription, summary, TTS, and video creation.

Dependencies (install via pip):
    yt-dlp
    requests
    python-dotenv
    openai
    moviepy

Environment Variables:
    ASSEMBLYAI_API_KEY
    OPENAI_API_KEY
"""
import os
import time
import tempfile
from typing import Dict, Optional, Tuple

import yt_dlp
import requests
from dotenv import load_dotenv
from openai import OpenAI
from moviepy.editor import AudioFileClip, ColorClip, TextClip, CompositeVideoClip
from moviepy.video.fx.speedx import speedx as video_speedx


class PodcastVideoGenerator:
    def __init__(self, assemblyai_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        load_dotenv()
        self.assemblyai_api_key = assemblyai_api_key or os.getenv(
            "ASSEMBLYAI_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.assemblyai_api_key or not self.openai_api_key:
            raise RuntimeError(
                "Both ASSEMBLYAI_API_KEY and OPENAI_API_KEY must be set")

        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.assemblyai_headers = {
            "Authorization": self.assemblyai_api_key, "Content-Type": "application/json"}
        self.transcribe_endpoint = "https://api.assemblyai.com/v2/transcript"

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

    def transcribe_audio_url(self, audio_url: str, poll_interval: int = 5, timeout: int = 600) -> str:
        payload = {"audio_url": audio_url}
        response = requests.post(
            self.transcribe_endpoint, json=payload, headers=self.assemblyai_headers)
        response.raise_for_status()
        job_id = response.json().get("id")

        start = time.time()
        while True:
            status_resp = requests.get(
                f"{self.transcribe_endpoint}/{job_id}", headers=self.assemblyai_headers)
            status_resp.raise_for_status()
            data = status_resp.json()
            if data.get('status') == 'completed':
                return data.get('text', '')
            if data.get('status') == 'error':
                raise RuntimeError(data.get('error', 'Transcription error'))
            if time.time() - start > timeout:
                raise TimeoutError("Transcription timed out")
            time.sleep(poll_interval)

    def download_and_transcribe(self, youtube_url: str) -> Tuple[str, Dict]:
        meta = self.get_youtube_metadata(youtube_url)
        with tempfile.TemporaryDirectory() as tmpdir:
            opts = {'format': 'bestaudio/best', 'outtmpl': f"{tmpdir}/audio"}
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([youtube_url])
            audio_file = next((f for f in os.listdir(tmpdir)
                              if f.startswith('audio')), None)
            if not audio_file:
                raise FileNotFoundError("Downloaded audio not found")
            audio_path = os.path.join(tmpdir, audio_file)
            # upload to AssemblyAI
            with open(audio_path, 'rb') as f:
                upload = requests.post('https://api.assemblyai.com/v2/upload', headers={
                                       'Authorization': self.assemblyai_api_key}, data=f)
            upload.raise_for_status()
            transcript = self.transcribe_audio_url(
                upload.json().get('upload_url'))
        return transcript, meta

    def summarize_text(self, text: str) -> str:
        resp = self.openai_client.chat.completions.create(
            model='gpt-4',
            messages=[
                {"role": "system", "content": "Summarize into concise bullet points without losing important details."},
                {"role": "user", "content": text}
            ],
            temperature=0.5
        )
        return resp.choices[0].message.content or ""

    def synthesize_speech(self, text: str, out_path: str) -> str:
        if os.path.exists(out_path):
            os.remove(out_path)
        audio = self.openai_client.audio.speech.create(
            model='tts-1', voice='alloy', input=text)
        audio.stream_to_file(out_path)
        return out_path

    def create_scrolling_video(self, summary: str, audio_path: str, video_path: str) -> str:
        s = self.video_settings
        clip_audio = AudioFileClip(audio_path)
        duration = clip_audio.duration
        total = (s['delay'] + duration + s['tail']) * s['speed_factor']
        bg = ColorClip((s['width'], s['height']),
                       color=s['bg_color'], duration=total)
        txt = TextClip(summary, fontsize=s['font_size'], color=s['text_color'], size=(
            s['text_width'], None), method='caption')
        h, w = txt.h, txt.w
        x0 = (s['width'] - w) // 2
        def pos(t): return (x0, s['height'] - (s['height'] + h) * (t/total))
        mov = txt.set_position(pos).set_duration(total)
        video = CompositeVideoClip([bg, mov]).fx(
            video_speedx, factor=s['speedup_factor'])
        audio_clip = clip_audio.set_start(s['delay']/s['speedup_factor'])
        final = video.set_audio(audio_clip)
        if os.path.exists(video_path):
            os.remove(video_path)
        final.write_videofile(video_path, fps=s['fps'], codec='libx264',
                              audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)
        return video_path

    def generate_video_from_url(self, youtube_url: str, output_dir: str = 'output') -> Dict[str, object]:
        os.makedirs(output_dir, exist_ok=True)
        transcript, meta = self.download_and_transcribe(youtube_url)
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
