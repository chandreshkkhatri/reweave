import moviepy.editor as mp

class BaseComponentClip:
    def init(self):
        self.clip: mp.VideoClip = None

    def get_clip(self):
        return self.clip

    def get_frame(self, t):
        return self.clip.get_frame(t)

    def get_duration(self):
        return self.clip.duration