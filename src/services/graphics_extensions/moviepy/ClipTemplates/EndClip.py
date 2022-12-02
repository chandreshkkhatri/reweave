import moviepy.editor as mp
from src.commons.enums.attributes import Position
from src.services.graphics_extensions.moviepy.ClipTemplates.BaseTemplateClip import BaseTemplateClip

class EndClip(BaseTemplateClip):
    def __init__(self, template, text, start_time) -> None:
        size = (template.aspect_ratio[0]*3/4, template.aspect_ratio[1]*7/8)
        clip = mp.TextClip(text,
                           size=size,
                           font=template.font_family,
                           color=template.font_color,
                           fontsize=template.font_size,
                           interline=20,
                           method=template.text_clip_method)
        clip = clip.set_duration(template.end_clip_duration).set_start(
            start_time, change_end=True)
        clip = clip.set_position((Position.CENTER.value, Position.CENTER.value))
        self.clip = clip
