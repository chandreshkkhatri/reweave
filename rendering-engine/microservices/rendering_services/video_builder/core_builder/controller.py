# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 10:22:35 2022

@author: Khatri
"""
from csv import reader
from commons.config import config

from microservices.rendering_services.video_builder.core_builder.builder import VideoBuilder

STANDARD_SHORT_ASPECT_RATIO = (900, 1600)
WHITE_COLOR = (0, 0, 0)

MP4 = 'mp4'
LIBX264 = 'libx264'
H264_QSV = 'h264_qsv'
DEFAULT_FPS = 24
BUILDS_DIR = "builds"
UTF_8 = 'utf8'


async def create_video_file(template, content, file_name):
    '''
    create video file from content
    '''
    video_builder = VideoBuilder()
    final_clip = await video_builder.get_video_clip(content, template)
    final_clip.write_videofile(
        f'{config.RESOURCES_DIR}/{BUILDS_DIR}/{file_name}.{MP4}', fps=DEFAULT_FPS, codec=H264_QSV)

def preview_video_file(template, content):
    '''
    preview video file from content
    '''
    video_builder = VideoBuilder(template)
    final_clip = video_builder.get_video_clip(content)
    final_clip.resize(height=540).preview()
