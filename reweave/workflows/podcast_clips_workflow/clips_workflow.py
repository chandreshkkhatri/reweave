"""
Podcast Highlight Clips Workflow

Extracts the best moments from a podcast and generates individual short-form clips:
  1. Fetch transcript from YouTube
  2. Gemini identifies the N most clip-worthy segments
  3. TTS generates narration for each clip
  4. Assembler creates vertical video for each clip
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

from reweave.ai.gemini_service import generate_audio
from reweave.utils.fs_utils import write_content_to_file
from reweave.workflows.base_workflow import BaseWorkflow

from .clip_extractor import extract_clips
from .clip_assembler import assemble_clip

OUTPUT_DIR = Path('data/output/podcast_clips')


class PodcastClipsWorkflow(BaseWorkflow):
    """Workflow for generating short-form clips from podcast episodes."""

    @property
    def workflow_name(self) -> str:
        return "Podcast Highlight Clips"

    @property
    def output_dir_prefix(self) -> str:
        return "podcast_clips"

    def generate(self, content_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate podcast highlight clips.

        Args:
            content_id: Unique identifier for this content piece.
            url: YouTube podcast URL.
            num_clips: Number of clips to extract (default: 5).

        Returns:
            Dict with paths to all generated outputs.
        """
        url = kwargs.get("url", "")
        num_clips = kwargs.get("num_clips", 5)
        return self.generate_clips(content_id, url, num_clips)

    def _get_youtube_metadata(self, youtube_url):
        """Fetch YouTube video metadata."""
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
        if not info:
            raise ValueError("Failed to extract YouTube metadata")
        return {
            'title': info.get('title', 'Unknown Podcast'),
            'uploader': info.get('uploader', ''),
        }

    def _get_transcript(self, youtube_url, languages=None):
        """Fetch transcript from YouTube."""
        if languages is None:
            languages = ['en']
        video_id = youtube_url.split('v=')[-1].split('&')[0]
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=languages)
        return '\n'.join(item.text for item in transcript)

    def generate_clips(self, content_id, youtube_url, num_clips=5):
        """
        Full pipeline: fetch transcript → extract highlights → generate clips.

        Args:
            content_id: Unique identifier for this content piece.
            youtube_url: YouTube podcast URL.
            num_clips: Number of clips to extract.

        Returns:
            Dict with paths to generated files and manifest.
        """
        output_dir = f"{OUTPUT_DIR}/{content_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: Fetch metadata and transcript
        meta = self._get_youtube_metadata(youtube_url)
        podcast_title = meta['title']
        print(f"Fetching transcript for: {podcast_title}")

        transcript = self._get_transcript(youtube_url)
        write_content_to_file(transcript, "transcript.txt", output_dir)
        print(f"Transcript fetched ({len(transcript)} chars)")

        # Step 2: Extract highlights
        manifest = extract_clips(transcript, podcast_title, youtube_url, num_clips)
        write_content_to_file(
            json.dumps(manifest.model_dump(), indent=2),
            "manifest.json",
            output_dir,
        )
        print(f"Extracted {len(manifest.clips)} clips")

        # Step 3: Generate TTS and video for each clip
        clip_paths = []
        for clip in manifest.clips:
            clip_dir = os.path.join(output_dir, f"clip_{clip.clip_number}")
            os.makedirs(clip_dir, exist_ok=True)

            # Generate TTS
            audio_path = os.path.join(clip_dir, "narration.mp3")
            audio = generate_audio(clip.narration_text)
            audio.stream_to_file(audio_path)

            # Save caption
            caption = f"{clip.topic_title}\n\nFrom: {podcast_title}\n\n#podcast #highlights #shorts"
            write_content_to_file(caption, "caption.txt", clip_dir)

            # Assemble video
            video_path = os.path.join(clip_dir, "clip.mp4")
            assemble_clip(
                clip.topic_title, clip.narration_text, audio_path, video_path
            )
            print(f"  Clip {clip.clip_number}: {clip.topic_title}")

            clip_paths.append({
                "number": clip.clip_number,
                "title": clip.topic_title,
                "video": video_path,
                "audio": audio_path,
                "caption": os.path.join(clip_dir, "caption.txt"),
            })

        return {
            "clips": clip_paths,
            "manifest": os.path.join(output_dir, "manifest.json"),
            "transcript": os.path.join(output_dir, "transcript.txt"),
            "podcast_title": podcast_title,
        }
