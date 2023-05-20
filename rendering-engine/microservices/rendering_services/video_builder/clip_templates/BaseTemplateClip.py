import moviepy.editor as mp

class BaseTemplateClip:
    def init(self):
        self.clip: mp.VideoClip = None

    def get_frame(self, t):
        return self.clip.get_frame(t)

    def get_duration(self):
        return self.clip.duration
