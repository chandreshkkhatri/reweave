"""
Podcast Summary Workflow

Orchestrates transcription, summarization, TTS, and video generation for podcast URLs.

Requires:
- podcast_video_generator.py in same directory
- Environment variables: GEMINI_API_KEY
"""
from typing import Dict

from .podcast_video_generator import PodcastVideoGenerator


class PodcastSummaryWorkflow:
    """
    Workflow for converting a podcast URL into a summary video.
    """

    def __init__(self):
        self.generator = PodcastVideoGenerator()

    def generate(self, youtube_url: str, output_dir: str = "output",
                 use_audio_transcription: bool = True) -> Dict[str, object]:
        """
        Run the full pipeline:
            1. Transcribe podcast audio from YouTube
            2. Generate bullet-point summary
            3. Create TTS narration audio
            4. Produce a scrolling-text video

        Args:
            youtube_url: The YouTube podcast URL to process
            output_dir: Directory to store outputs
            use_audio_transcription: If True, download audio and transcribe with
                Gemini for better accuracy. Falls back to YouTube captions on failure.

        Returns:
            A dict containing paths to video, audio, transcript, and summary
        """
        return self.generator.generate_video_from_url(
            youtube_url, output_dir,
            use_audio_transcription=use_audio_transcription,
        )
