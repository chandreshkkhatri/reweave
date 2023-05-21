import moviepy.editor as mp
import app.services.rendering_services.graphics_extensions.moviepy.ClipComponents as cc
from app.services.rendering_services.graphics_extensions.moviepy.ClipComponents.BaseComponentClip import BaseComponentClip


class SubtitleClip(BaseComponentClip):
    def __init__(self, template, subtitle, start_time):
        self.__template = template
        clip = cc.TypingEffectClip(template=template,
                                   text=subtitle,
                                   size=(
                                       self.__template.aspect_ratio[0], self.__template.font_size*4),
                                   start_time=start_time
                                   )
        clip = clip.on_color(color=(255, 255, 255), col_opacity=0.6, size=(
            self.__template.aspect_ratio[0], self.__template.font_size*2))
        clip = clip.set_position(("center", "bottom"))
        clip = clip.set_duration(self.__template.subclip_duration)
        clip = clip.set_start(start_time, change_end=True)
        self.clip = clip
