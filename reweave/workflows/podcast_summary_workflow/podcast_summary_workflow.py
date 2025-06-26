"""
Podcast Summary Workflow

Orchestrates transcription, summarization, TTS, and video generation for podcast URLs.

Requires:
- podcast_video_generator.py in same directory
- Environment variables: ASSEMBLYAI_API_KEY, OPENAI_API_KEY
"""
from typing import Dict, Optional

from .podcast_video_generator import PodcastVideoGenerator


class PodcastSummaryWorkflow:
    """
    Workflow for converting a podcast URL into a summary video.
    """

    def __init__(self,
                 assemblyai_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Args:
            assemblyai_api_key: AssemblyAI API key or None to use env var
            openai_api_key: OpenAI API key or None to use env var
        """
        # Initialize the underlying video generator
        self.generator = PodcastVideoGenerator(
            assemblyai_api_key=assemblyai_api_key,
            openai_api_key=openai_api_key
        )

    from typing import Mapping

    def generate(self, youtube_url: str, output_dir: str = "output") -> Mapping[str, object]:
        """
        Run the full pipeline:
            1. Transcribe podcast audio from YouTube
            2. Generate bullet-point summary
            3. Create TTS narration audio
            4. Produce a scrolling-text video

        Args:
            youtube_url: The YouTube podcast URL to process
            output_dir: Directory to store outputs

        Returns:
            A dict containing paths to video, audio, transcript, and summary
        """
        return self.generator.generate_video_from_url(youtube_url, output_dir)
