"""
audio_clip.py
This file contains the AudioClip class, which is used to create an audio clip for the video.
"""
import moviepy.editor as mp
from app.components.clip_components.base_clip_component import BaseComponentClip


class AudioClip(BaseComponentClip):
    """
    AudioClip
    This class is used to create an audio clip for the video.
    """
    def __init__(self, template, use_terminal_audio, clip_duration):
        self.__template = template
        audio_clip = mp.AudioFileClip(
            filename=self.__template.background_audio).subclip(4, clip_duration)
        if use_terminal_audio:
            terminal_audio_music = mp.AudioFileClip(
                filename=self.__template.terminal_clip_audio)
            terminal_audio_clip = mp.afx.audio_loop(terminal_audio_music,
                                duration=self.__template.subclip_duration).set_start(
                clip_duration - self.__template.subclip_duration)
            audio_clip = audio_clip.set_duration(
                clip_duration - self.__template.subclip_duration)
            audio_clip = mp.CompositeAudioClip(
                [audio_clip, terminal_audio_clip])
        else:
            audio_clip = audio_clip.set_duration(clip_duration)
        self.clip = audio_clip
