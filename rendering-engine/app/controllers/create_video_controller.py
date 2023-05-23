from typing import List

from app.commons.classes.dataclasses import ClipContent, VideoTemplate
from app.services.rendering_services.video_builder.core_builder.builder import VideoBuilder
from app.services.rendering_services.video_builder.core_builder.helper import get_template


class CreateVideoController:
    """
    Create video controller
    """

    def __init__(self):
        '''
        initialize create video controller
        '''
        self.__template: VideoTemplate = None

    async def get_video_clip(self, content_list: List, video_template: VideoTemplate, use_terminal_audio=False):
        """
        create video clip from content and template
        """
        self.__template = await get_template(video_template)
        content_list = [self.get_content_from_dict(
            content) for content in content_list]
        builder = VideoBuilder()
        return builder.build_video(content_list=content_list,
                                   template=self.__template, use_terminal_audio=use_terminal_audio)

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
