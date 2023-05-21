"""
Build Video from Content and template
"""
from typing import List
import moviepy.editor as mp
from moviepy.audio.fx import all as afx
from app.services.rendering_services.text_to_speech import pytts
from app.services.rendering_services.video_builder.core_builder.helper import get_template
from app.services.rendering_services.video_builder import clip_templates as ct
from app.services.rendering_services.graphics_extensions.moviepy import ClipComponents as cc
from app.commons.classes.dataclasses import VideoTemplate, ClipContent
from app.commons.enums import ClipType


class VideoBuilder:
    """
    Build video clip from content and template
    """

    def __init__(self):
        '''
        initialize video builder
        '''
        self.__audio_clip: mp.AudioClip = None
    
    async def get_video_clip(self, content_list: List, video_template: VideoTemplate, use_terminal_audio=False):
        """
        create video clip from content and template
        """
        self.__template = await get_template(video_template)
        content_list = [self.get_content_from_dict(
            content) for content in content_list]
        return self.__build_video(content_list, use_terminal_audio)

    def __build_video(self, content_list: List[ClipContent], use_terminal_audio=False):
        '''
        build video from content list
        '''
        self.__set_content_attributes(content_list=content_list)
        self.__clips_list = []
        self.__text_to_speech_clips: List[mp.AudioClip] = []
        self.__current_clip_duration = 0
        self.__page_number = 0
        self.__add_background_color_clip()
        self.__add_background_image_clip()
        for clip_content in content_list:
            if clip_content.text:
                clip_content.text = clip_content.text.strip()
            if clip_content.type == ClipType.COVER_CLIP:
                self.__add_cover_clip(clip_content)
            elif clip_content.type == ClipType.TITLE_CLIP:
                self.__add_title_clip(clip_content)
            elif clip_content.type == ClipType.END_CLIP:
                self.__add_end_clip(clip_content)
            else:
                if clip_content.type == ClipType.IMAGE_CLIP:
                    self.__add_image_clip(clip_content)
                elif clip_content.type == ClipType.SCROLLING_TEXT_CLIP:
                    self.__add_scrolling_text_clip(clip_content)
                else:
                    self.__add_text_clip(clip_content)
                if clip_content.subtitle:
                    self.__add_subtitle_clip(clip_content)

        composed_video: mp.VideoClip = mp.CompositeVideoClip(self.__clips_list)
        composed_video: mp.VideoClip = composed_video.set_fps(24)
        self.__set_audio_clip(use_terminal_audio)
        composed_video: mp.VideoClip = composed_video.set_audio(
            self.__audio_clip)
        final_clip: mp.VideoClip = composed_video.subclip(
            0, self.__current_clip_duration)

        return final_clip

    def __set_content_attributes(self, content_list: List[ClipContent]):
        '''
        set content attributes
        '''
        content_length = 0
        for content in content_list:
            if content.type == ClipType.TEXT_CLIP or content.type == ClipType.IMAGE_CLIP or content.type == ClipType.SCROLLING_TEXT_CLIP:
                content_length += 1
        self.__content_length = content_length

    def __add_background_color_clip(self):
        '''
        add background color clip to video
        '''
        bg_color_clip = mp.ColorClip(size=self.__template.aspect_ratio,
                                     color=self.__template.background_color,
                                     )
        self.__clips_list.append(bg_color_clip)

    def __add_background_image_clip(self):
        '''
        add background image clip to video
        '''
        if self.__template.use_background_image:
            background_clip = mp.ImageClip(
                img=self.__template.background_image, duration=self.__template.duration)
            self.__clips_list.append(background_clip)

    def __add_cover_clip(self, clip_content: ClipContent):
        '''
        add cover clip to video
        '''
        clip = ct.CoverClip(
            self.__template, clip_content, self.__current_clip_duration).clip
        self.__current_clip_duration += clip_content.duration
        self.__clips_list.append(clip)

    def __add_title_clip(self, clip_content: ClipContent):
        '''
        add title clip to video
        '''
        clip = ct.TitleClip(
            self.__template, clip_content.text, self.__current_clip_duration).clip
        self.__current_clip_duration += self.__template.title_clip_duration
        self.__clips_list.append(clip)

    def __add_end_clip(self, clip_content: ClipContent):
        '''
        add end clip to video
        '''
        clip = ct.EndClip(
            self.__template, clip_content.text, self.__current_clip_duration, clip_content.duration).clip
        self.__current_clip_duration += clip_content.duration
        self.__clips_list.append(clip)

    def __add_text_clip(self, clip_content: ClipContent):
        '''
        add text clip to video
        '''
        if clip_content.text_to_speech:
            pytts.save_audio(clip_content.text, clip_content.tts_fn)
            audio_clip = mp.AudioFileClip(clip_content.tts_fn)
            audio_clip: mp.AudioClip = afx.volumex(audio_clip, 0.7)
            audio_clip: mp.AudioClip = audio_clip.set_start(self.__current_clip_duration)
            self.__text_to_speech_clips.append(audio_clip)
            clip_duration = audio_clip.duration
        else:
            clip_duration = clip_content.duration
        clip: mp.TextClip = ct.TextClip(
            self.__template, clip_content.text, self.__current_clip_duration, clip_content.duration).clip
        self.__add_page_number_clip(clip_duration)
        self.__current_clip_duration += clip_duration
        self.__clips_list.append(clip)

    def __add_scrolling_text_clip(self, clip_content: ClipContent):
        '''
        add scrolling text clip to video
        '''
        scrolling_clip = ct.ScrollingTextClip(
            self.__template, clip_content, self.__current_clip_duration)
        self.__add_page_number_clip(scrolling_clip.duration)
        self.__current_clip_duration += scrolling_clip.duration
        self.__clips_list.append(scrolling_clip.clip)

    def __add_image_clip(self, clip_content: ClipContent):
        '''
        add image clip to video
        '''
        clip = ct.ImageClip(
            self.__template, clip_content.image_file_name, self.__current_clip_duration).clip
        resize_factor = (self.__template.aspect_ratio[0]/clip.size[0])*3/4
        duration = self.__template.subclip_duration
        self.__add_page_number_clip(duration)
        self.__current_clip_duration += duration
        clip: mp.VideoClip = clip.resize(resize_factor)
        self.__clips_list.append(clip)

    def __add_page_number_clip(self, duration):
        '''
        add page number clip to video
        '''
        page_number_clip = cc.PageNumberClip(
            self.__template, self.__page_number, self.__content_length, self.__current_clip_duration, duration).clip
        self.__page_number = self.__page_number + 1
        self.__clips_list.append(page_number_clip)

    def __add_subtitle_clip(self, clip_content: ClipContent):
        '''
        add subtitle clip to video
        '''
        clip = cc.SubtitleClip(
            self.__template, clip_content.subtitle, self.__current_clip_duration).clip
        self.__clips_list.append(clip)

    def __set_audio_clip(self, use_terminal_audio):
        '''
        set audio clip to video
        '''
        audio_clip = cc.AudioClip(
            self.__template, use_terminal_audio, self.__current_clip_duration).clip
        if len(self.__text_to_speech_clips):
            audio_clips = []
            last_clip_end = 0
            for clip in self.__text_to_speech_clips:
                if clip.start > last_clip_end:
                    audio_clips.append(audio_clip.subclip(
                        last_clip_end, clip.start))
                audio_subclip = audio_clip.subclip(clip.start, clip.end)
                audio_subclip = afx.volumex(
                    audio_subclip, 0.3).set_start(clip.start)
                audio_subclip = audio_subclip.set_end(clip.end)
                audio_clips.extend([audio_subclip, clip])
                last_clip_end = clip.end
            self.__audio_clip = mp.CompositeAudioClip(audio_clips)
        else:
            self.__audio_clip = audio_clip

    def get_content_from_dict(self, content_dict: dict):
        '''
        get content from dict
        '''
        clip_content = ClipContent(
            type=content_dict.get('type'),
            text=content_dict.get('text'),
            image_file_name=content_dict.get('image_file_name'),
        )
        return clip_content
