import moviepy.editor as mp
from microservices.rendering_services.video_builder.clip_templates.BaseTemplateClip import BaseTemplateClip
from commons.config import config


class CoverClip(BaseTemplateClip):
    def __init__(self, template, content,  start_time) -> None:
        self.template = template
        image_path = f"{config.RESOURCES_DIR}/assets/Covers/{content.image_file_name}"
        img_clip = mp.ImageClip(image_path)
        cover_txt = content.text.replace('\\n', '\n') if content.text else ''
        w, h = self.template.aspect_ratio[0], self.template.aspect_ratio[1]

        txt_clip = mp.TextClip(cover_txt,
                               size=(w*3/4, h*7/8),
                               font=self.template.font_family,
                               color=self.template.font_color,
                               fontsize=self.template.cover_font_size,
                               interline=20,
                               method=self.template.text_clip_method)
        txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(
            content.duration)
        clip = mp.CompositeVideoClip([img_clip, txt_clip])
        clip = clip.set_position((0, 0))
        clip = clip.set_duration(content.duration).set_start(
            start_time, change_end=True)
        self.clip = clip
