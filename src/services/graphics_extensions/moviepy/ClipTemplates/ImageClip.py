import moviepy.editor as mp
from commons.enums.attributes import Position
from src.services.graphics_extensions.moviepy.ClipTemplates.BaseTemplateClip import BaseTemplateClip


class ImageClip(BaseTemplateClip):
    def __init__(self, template, image_path, start_time):
        clip = mp.ImageClip(image_path)
        clip = clip.set_position((Position.CENTER.value, Position.CENTER.value))
        clip = clip.set_duration(template.subclip_duration)
        clip = clip.set_start(start_time, change_end=True)
        self.clip = clip
