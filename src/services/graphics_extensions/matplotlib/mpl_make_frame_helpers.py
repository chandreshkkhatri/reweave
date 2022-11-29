import numpy as np
import moviepy.editor as mp
from moviepy.video.io.bindings import mplfig_to_npimage
from src.services.graphics_extensions.matplotlib.core_builder import CoreBuilder


class MPLMakeFrameHelpers(CoreBuilder):
    def __init__(self) -> None:
        super().__init__()

    def preview_mp_clip(self, make_frame, duration):
        print (duration, 'duration')
        animation = mp.VideoClip(make_frame, duration=duration)
        animation.preview(fps=30)

    def get_mp_clip(self, make_frame, duration):
        return mp.VideoClip(make_frame, duration)
