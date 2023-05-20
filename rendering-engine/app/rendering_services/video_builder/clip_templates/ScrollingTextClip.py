import moviepy.editor as mp
import app.rendering_services.graphics_extensions.moviepy.ClipComponents as ct
from app.rendering_services.video_builder.clip_templates.BaseTemplateClip import BaseTemplateClip


class ScrollingTextClip(ct.ScrollingTextClip):
    def __init__(self, template, clip_content, start_time) -> None:
        super().__init__(template, clip_content, start_time, split_text=True)
