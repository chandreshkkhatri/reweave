"""
Quote Assembler

Composites quote text over a background image to produce:
- 1080x1080 square PNG (Instagram feed)
- 1080x1920 vertical PNG (Instagram story)
- 15-second Ken Burns MP4 with TTS (TikTok/Reels)
"""

import os

from moviepy import ImageClip, TextClip, ColorClip, CompositeVideoClip, AudioFileClip

from reweave.utils.video_utils import DEFAULT_FONT


SQUARE_SIZE = 1080
VERTICAL_WIDTH = 1080
VERTICAL_HEIGHT = 1920
VIDEO_DURATION = 15
FPS = 24


def _composite_quote_on_image(image_path, quote_text, attribution, width, height):
    """
    Composite quote text over an image with a dark overlay.

    Returns a CompositeVideoClip frame (duration=0, used for still image export).
    """
    img_clip = ImageClip(image_path).resized((width, height))

    overlay = ColorClip((width, height), color=(0, 0, 0)).with_opacity(0.45)

    quote_clip = TextClip(
        font=DEFAULT_FONT,
        text=f'"{quote_text}"',
        font_size=48 if len(quote_text) < 100 else 38,
        color='white',
        size=(int(width * 0.80), None),
        method='caption',
    ).with_position(('center', height * 0.35))

    attr_clip = TextClip(
        font=DEFAULT_FONT,
        text=f"— {attribution}",
        font_size=30,
        color='#cccccc',
        size=(int(width * 0.80), None),
        method='caption',
    ).with_position(('center', height * 0.65))

    composite = CompositeVideoClip(
        [img_clip, overlay, quote_clip, attr_clip],
        size=(width, height),
    )
    return composite


def generate_square_image(image_path, quote_text, attribution, output_path):
    """Generate a 1080x1080 square quote card PNG."""
    composite = _composite_quote_on_image(
        image_path, quote_text, attribution, SQUARE_SIZE, SQUARE_SIZE
    )
    composite.save_frame(output_path, t=0)
    composite.close()
    return output_path


def generate_story_image(image_path, quote_text, attribution, output_path):
    """Generate a 1080x1920 vertical story quote card PNG."""
    composite = _composite_quote_on_image(
        image_path, quote_text, attribution, VERTICAL_WIDTH, VERTICAL_HEIGHT
    )
    composite.save_frame(output_path, t=0)
    composite.close()
    return output_path


def generate_video(image_path, quote_text, attribution, audio_path, output_path):
    """
    Generate a 15-second Ken Burns zoom video with TTS narration.

    The background image slowly zooms from 1.0x to 1.08x over the duration.
    """
    duration = VIDEO_DURATION

    img_clip = (
        ImageClip(image_path)
        .with_duration(duration)
        .resized(lambda t: 1 + 0.08 * (t / duration))
        .resized((VERTICAL_WIDTH, VERTICAL_HEIGHT))
    )

    overlay = (
        ColorClip((VERTICAL_WIDTH, VERTICAL_HEIGHT), color=(0, 0, 0))
        .with_opacity(0.45)
        .with_duration(duration)
    )

    quote_clip = TextClip(
        font=DEFAULT_FONT,
        text=f'"{quote_text}"',
        font_size=48 if len(quote_text) < 100 else 38,
        color='white',
        size=(int(VERTICAL_WIDTH * 0.80), None),
        method='caption',
    ).with_duration(duration).with_position(('center', VERTICAL_HEIGHT * 0.35))

    attr_clip = TextClip(
        font=DEFAULT_FONT,
        text=f"— {attribution}",
        font_size=30,
        color='#cccccc',
        size=(int(VERTICAL_WIDTH * 0.80), None),
        method='caption',
    ).with_duration(duration).with_position(('center', VERTICAL_HEIGHT * 0.65))

    video = CompositeVideoClip(
        [img_clip, overlay, quote_clip, attr_clip],
        size=(VERTICAL_WIDTH, VERTICAL_HEIGHT),
    )

    audio_clip = AudioFileClip(audio_path)
    video = video.with_audio(audio_clip)

    video.write_videofile(
        output_path, fps=FPS, codec='libx264',
        audio_codec='aac', temp_audiofile='temp-quote-audio.m4a',
        remove_temp=True,
    )
    video.close()
    return output_path
