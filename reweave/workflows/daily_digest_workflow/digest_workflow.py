"""
Daily Digest Workflow

Orchestrates the generation of short-form vertical digest videos:
  1. GPT-4 generates structured digest content (title, bullets, narration, image prompt)
  2. DALL-E generates hero background image
  3. TTS generates narration audio
  4. Assembler creates vertical video with animated bullet points
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

from reweave.ai.gemini_service import generate_image
from reweave.utils.fs_utils import write_content_to_file, write_bytes_to_file
from reweave.utils.audio_utils import chunk_and_generate_tts
from reweave.workflows.base_workflow import BaseWorkflow

from .digest_builder import build_digest
from .digest_assembler import assemble_digest_video

OUTPUT_DIR = Path('data/output/daily_digest')


class DailyDigestWorkflow(BaseWorkflow):
    """Workflow for generating short-form vertical digest videos."""

    @property
    def workflow_name(self) -> str:
        return "Daily Digest"

    @property
    def output_dir_prefix(self) -> str:
        return "daily_digest"

    def generate(self, content_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a daily digest video.

        Args:
            content_id: Unique identifier for this content piece.
            topic: Topic for the digest (e.g., "AI breakthroughs this week").

        Returns:
            Dict with paths to all generated outputs.
        """
        topic = kwargs.get("topic", "technology news")
        return self.generate_digest(content_id, topic)

    def generate_digest(self, content_id, topic):
        """
        Full pipeline: build digest → generate assets → assemble video.

        Args:
            content_id: Unique identifier for this content piece.
            topic: Topic for the digest.

        Returns:
            Dict with paths to generated files and metadata.
        """
        output_dir = f"{OUTPUT_DIR}/{content_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: Generate digest content
        digest = build_digest(topic)
        write_content_to_file(
            json.dumps(digest.model_dump(), indent=2),
            "digest_data.json",
            output_dir,
        )
        print(f"Generated digest: {digest.title}")
        print(f"  {len(digest.bullets)} bullet points")

        # Step 2: Generate background image
        image_bytes = generate_image(digest.image_prompt)
        image_path = os.path.join(output_dir, "background.png")
        write_bytes_to_file(image_bytes, "background.png", output_dir)
        print("Generated background image")

        # Step 3: Generate TTS narration
        audio_path = os.path.join(output_dir, "narration.mp3")
        chunk_and_generate_tts(digest.narration, audio_path)
        print("Generated narration audio")

        # Step 4: Assemble video
        video_path = os.path.join(output_dir, "digest_video.mp4")
        bullet_texts = [b.text for b in digest.bullets]
        assemble_digest_video(
            image_path, audio_path, digest.title, bullet_texts, video_path
        )
        print("Generated digest video (1080x1920)")

        # Step 5: Save caption and thumbnail
        write_content_to_file(digest.caption, "caption.txt", output_dir)

        return {
            "video": video_path,
            "audio": audio_path,
            "background": image_path,
            "caption": os.path.join(output_dir, "caption.txt"),
            "metadata": os.path.join(output_dir, "digest_data.json"),
            "digest": digest.model_dump(),
        }
