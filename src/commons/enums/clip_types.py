"""Types of clips supported by the application."""

from enum import Enum, auto

class ClipType(str,Enum):
    """Types of clips supported by the application."""
    COVER_CLIP = 'cover_clip'
    TITLE_CLIP = 'title_clip'
    END_CLIP = 'end_clip'
    CONTENT_CLIP = 'content_clip'
    SUBTITLE_CLIP = 'subtitle_clip'
    SCROLLING_TEXT_CLIP = 'scrolling_text_clip'
    IMAGE_CLIP = 'image_clip'
