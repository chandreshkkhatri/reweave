import moviepy.editor as mp
from app.commons.classes.dataclasses import VideoTemplate
from app.commons.enums.attributes import Position
import app.rendering_services.graphics_extensions.moviepy.ClipComponents as cc
from app.rendering_services.video_builder.clip_templates.BaseTemplateClip import BaseTemplateClip


class TextClip(BaseTemplateClip):
    def __init__(self, template: VideoTemplate, text, start_time, duration, use_effect=None) -> None:
        self.template = template
        self.subclip_duration = duration
        text = text.replace('\\n', '\n') if text else ''
        if use_effect:
            w, h = self.template.aspect_ratio[0], self.template.aspect_ratio[1]
            text_clip = cc.TypingEffectClip(
                self.template, (w*3/4, h*7/8), text, start_time)
            self.clip = text_clip
        else:
            self.create_text_clip(text, start_time)

    def create_text_clip(self, text, start_time):
        """get TextClip from content"""
        w, h = self.template.aspect_ratio[0], self.template.aspect_ratio[1]
        clip = mp.TextClip(text,
                           size=(w*3/4, h),
                           font=self.template.font_family,
                           color=self.template.font_color,
                           fontsize=self.template.font_size,
                           interline=20,
                           method=self.template.text_clip_method)
        clip = clip.set_duration(self.subclip_duration).set_start(
            start_time, change_end=True)
        clip = clip.set_position((Position.CENTER.value, Position.CENTER.value))
        self.clip = clip
