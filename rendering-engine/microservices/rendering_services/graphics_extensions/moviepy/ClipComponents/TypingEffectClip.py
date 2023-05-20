import moviepy.editor as mp
from microservices.rendering_services.graphics_extensions.moviepy.ClipComponents.BaseComponentClip import BaseComponentClip


class TypingEffectClip(BaseComponentClip):
    def __init__(self, template, size, text, start_time) -> None:
        self = self.__get_typing_effect_clip(text=text, speed=10,
                                           size=size,
                                           font=template.font_family,
                                           interline=20,
                                           color=template.font_color,
                                           fontsize=template.font_size,
                                           method=template.text_clip_method)
        self = self.set_start(start_time, change_end=True)

    def __get_typing_effect_clip(self, text, speed, **kwargs):
        """speed in characters per second"""
        char_dur = 1/speed
        clip_text = ''
        text_clips = []
        l = len(text)
        for i in range(l):
            char = text[i]
            clip_text += char
            subclip = mp.TextClip(
                txt=clip_text, **kwargs).set_duration(char_dur).set_start(i*char_dur, change_end=True)
            text_clips.append(subclip)
        subclip = mp.TextClip(txt=clip_text, **kwargs).set_start(l*char_dur)
        text_clips.append(subclip)
        return mp.CompositeVideoClip(text_clips)
