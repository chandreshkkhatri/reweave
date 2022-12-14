import moviepy.editor as mp
from src.services.graphics_extensions.moviepy.ClipTemplates.BaseTemplateClip import BaseTemplateClip


class CoverClip(BaseTemplateClip):
    def __init__(self, image_file_name, start_time, duration) -> None:
        image_path = "{RESOURCES_DIR}/assets/{image_file_name}"
        clip = mp.ImageClip(image_path)
        clip = clip.set_position((0, 0))
        clip = clip.set_duration(duration).set_start(
            start_time, change_end=True)
        self.clip = clip
