import moviepy.editor as mp
from src.services.graphics_extensions.moviepy.ClipComponents.BaseComponentClip import BaseComponentClip


class PageNumberClip(BaseComponentClip):
    def __init__(self, template, page_number, total_pages, start_time) -> None:
        clip = mp.TextClip(f"{page_number+1}/{total_pages}",
                           font=template.font_family,
                           color=template.font_color,
                           fontsize=template.font_size/2,
                           method=template.text_clip_method)
        clip = clip.set_duration(template.subclip_duration).set_start(
            start_time, change_end=True)
        clip = clip.set_position((100, 150))
        self.clip = clip
