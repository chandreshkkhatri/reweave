import moviepy.editor as mp
from app.commons.enums.attributes import Position
from app.services.rendering_services.video_builder.clip_templates.BaseTemplateClip import BaseTemplateClip


class TitleClip(BaseTemplateClip):
    def __init__(self, template, text, start_time) -> None:
        size = (template.aspect_ratio[0]*3/4, template.aspect_ratio[1]*7/8)
        clip = mp.TextClip(text,
                           size=size,
                           font=template.font_family,
                           color=template.font_color,
                           fontsize=template.font_size,
                           interline=20,
                           method=template.text_clip_method)
        clip = clip.set_duration(template.title_clip_duration).set_start(
            start_time, change_end=True)
        clip = clip.set_position((Position.CENTER.value, Position.CENTER.value))
        self.clip = clip
