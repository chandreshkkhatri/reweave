import moviepy.editor as mp
from src.services.graphics_extensions.moviepy.ClipTemplates.BaseTemplateClip import BaseTemplateClip


class CoverClip(BaseTemplateClip):
    def __init__(self, image, start_time, duration) -> None:
        clip = mp.ImageClip(image)
        clip = clip.set_position((0, 0))
        clip = clip.set_duration(duration).set_start(
            start_time, change_end=True)
        self.clip = clip
