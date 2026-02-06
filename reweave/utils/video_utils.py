"""
Video Utilities

Shared constants and helpers for video assembly, especially vertical short-form content.
"""

import os

from moviepy import TextClip, ColorClip, CompositeVideoClip


# Vertical video dimensions (TikTok, Reels, Shorts)
VERTICAL_WIDTH = 1080
VERTICAL_HEIGHT = 1920
FPS = 24

# Standard horizontal
HORIZONTAL_WIDTH = 1920
HORIZONTAL_HEIGHT = 1080

# Default font — auto-detected from common system paths
_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]

DEFAULT_FONT = None
for _font in _FONT_CANDIDATES:
    if os.path.exists(_font):
        DEFAULT_FONT = _font
        break


def create_title_card(text, duration=3, width=VERTICAL_WIDTH, height=VERTICAL_HEIGHT,
                      font_size=60, text_color='white', bg_color=(20, 20, 20)):
    """
    Create a simple title card clip with centered text on a colored background.

    Returns:
        A CompositeVideoClip of the title card.
    """
    bg = ColorClip((width, height), color=bg_color, duration=duration)
    txt = TextClip(
        font=DEFAULT_FONT,
        text=text,
        font_size=font_size,
        color=text_color,
        size=(int(width * 0.85), None),
        method='caption',
    ).with_duration(duration).with_position('center')
    return CompositeVideoClip([bg, txt])


def create_text_overlay(text, duration, width=VERTICAL_WIDTH, font_size=36,
                        text_color='white', position='center'):
    """
    Create a styled text clip for overlaying on images/backgrounds.

    Returns:
        A TextClip configured for compositing.
    """
    return TextClip(
        font=DEFAULT_FONT,
        text=text,
        font_size=font_size,
        color=text_color,
        size=(int(width * 0.85), None),
        method='caption',
    ).with_duration(duration).with_position(position)
