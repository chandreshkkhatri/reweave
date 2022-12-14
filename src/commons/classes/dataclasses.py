"""Config class definition"""

from ast import Num
from dataclasses import dataclass
from typing import Optional
from src.commons.enums import ClipType

STANDARD_SHORT_ASPECT_RATIO=(900,1600)
WHITE_COLOR = (0, 0, 0)

@dataclass
class VideoTemplate:
    """Class for Initializing a template for a video"""
    font_color: str
    font_family: str
    font_size: str
    title_font_size: str
    background_image: Optional[str]
    background_color: str
    text_clip_method: str
    text_clip_color_pos: str
    background_audio: str
    use_background_image: bool
    terminal_clip_audio: str
    duration: Num=30
    title_clip_duration: Num=5
    end_clip_duration: Num=5
    subclip_duration: Num=5
    aspect_ratio: tuple=STANDARD_SHORT_ASPECT_RATIO
    text_background_color=WHITE_COLOR
    

@dataclass
class ClipContent:
    """Class for Initializing a template for a video"""
    type: ClipType
    text: Optional[str] = ''
    text_to_speech: Optional[bool] = False
    image_file_name: Optional[str] = ''
    subtitle: Optional[str] = ''
    tts_fn: Optional[str] = ''
    duration: Optional[Num] = 5
    start_time: Optional[Num] = 0
