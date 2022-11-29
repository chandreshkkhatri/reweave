import moviepy.editor as mp
import src.services.graphics_extensions.moviepy.ClipComponents as ct
from src.services.graphics_extensions.moviepy.ClipTemplates.BaseTemplateClip import BaseTemplateClip


class ScrollingTextClip(ct.ScrollingTextClip):
    def __init__(self, template, text, start_time) -> None:
        super().__init__(template, text, start_time, split_text=True)
