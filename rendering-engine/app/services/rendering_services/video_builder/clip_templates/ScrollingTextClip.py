import moviepy.editor as mp
import app.components.clip_components as ct
from app.services.rendering_services.video_builder.clip_templates.BaseTemplateClip import BaseTemplateClip


class ScrollingTextClip(ct.ScrollingTextClip):
    def __init__(self, template, clip_content, start_time) -> None:
        super().__init__(template, clip_content, start_time, split_text=True)
