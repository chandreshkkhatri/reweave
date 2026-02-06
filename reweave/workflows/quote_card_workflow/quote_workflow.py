"""
Quote Card Workflow

Orchestrates the generation of inspirational quote cards:
  1. GPT-4 generates quote, image prompt, and caption
  2. DALL-E generates background image
  3. TTS generates quote narration
  4. Assembler composites outputs into image + video formats
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

from reweave.ai.gemini_service import generate_image, generate_audio
from reweave.utils.fs_utils import write_content_to_file, write_bytes_to_file
from reweave.workflows.base_workflow import BaseWorkflow

from .quote_builder import build_quote_card
from .quote_assembler import (
    generate_square_image,
    generate_story_image,
    generate_video,
)

OUTPUT_DIR = Path('data/output/quote_cards')


class QuoteCardWorkflow(BaseWorkflow):
    """Workflow for generating inspirational quote card content."""

    @property
    def workflow_name(self) -> str:
        return "Quote Cards"

    @property
    def output_dir_prefix(self) -> str:
        return "quote_cards"

    def generate(self, content_id: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a complete quote card set.

        Args:
            content_id: Unique identifier for this content piece.
            theme: Theme for the quote (e.g., "stoic wisdom", "monday motivation").

        Returns:
            Dict with paths to all generated outputs.
        """
        theme = kwargs.get("theme", "inspiration")
        return self.generate_quote_card(content_id, theme)

    def generate_quote_card(self, content_id, theme):
        """
        Full pipeline: build quote → generate assets → assemble outputs.

        Args:
            content_id: Unique identifier for this content piece.
            theme: Theme for the quote.

        Returns:
            Dict with paths to generated files and metadata.
        """
        output_dir = f"{OUTPUT_DIR}/{content_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: Generate quote content
        quote_card = build_quote_card(theme)
        write_content_to_file(
            json.dumps(quote_card.model_dump(), indent=2),
            "quote_data.json",
            output_dir,
        )
        print(f"Generated quote: \"{quote_card.quote_text}\" — {quote_card.attribution}")

        # Step 2: Generate background image
        image_bytes = generate_image(quote_card.image_prompt)
        image_path = os.path.join(output_dir, "background.png")
        write_bytes_to_file(image_bytes, "background.png", output_dir)
        print("Generated background image")

        # Step 3: Generate TTS narration
        audio_path = os.path.join(output_dir, "narration.mp3")
        tts_text = f"{quote_card.quote_text}. By {quote_card.attribution}."
        audio_stream = generate_audio(tts_text)
        audio_stream.stream_to_file(audio_path)
        print("Generated narration audio")

        # Step 4: Assemble outputs
        square_path = os.path.join(output_dir, "quote_square.png")
        generate_square_image(
            image_path, quote_card.quote_text, quote_card.attribution, square_path
        )
        print("Generated square image (1080x1080)")

        story_path = os.path.join(output_dir, "quote_story.png")
        generate_story_image(
            image_path, quote_card.quote_text, quote_card.attribution, story_path
        )
        print("Generated story image (1080x1920)")

        video_path = os.path.join(output_dir, "quote_video.mp4")
        generate_video(
            image_path, quote_card.quote_text, quote_card.attribution,
            audio_path, video_path,
        )
        print("Generated video (15s Ken Burns)")

        # Step 5: Save caption
        write_content_to_file(quote_card.caption, "caption.txt", output_dir)

        return {
            "square_image": square_path,
            "story_image": story_path,
            "video": video_path,
            "audio": audio_path,
            "caption": os.path.join(output_dir, "caption.txt"),
            "metadata": os.path.join(output_dir, "quote_data.json"),
            "quote": quote_card.model_dump(),
        }
