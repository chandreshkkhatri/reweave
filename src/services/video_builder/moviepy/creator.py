# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 10:22:35 2022

@author: Khatri
"""
from csv import reader

from src.services.video_builder.moviepy.builder import VideoBuilder

STANDARD_SHORT_ASPECT_RATIO = (900, 1600)
WHITE_COLOR = (0, 0, 0)

MP4 = 'mp4'
LIBX264 = 'libx264'
DEFAULT_FPS = 24
BUILDS_DIR = "builds"
UTF_8 = 'utf8'
class VideoCreator:
    """Video Builder Class"""

    def create_video_files(self, template, file_name: str):
        '''
        create video files from csv file
        '''
        video_builder = VideoBuilder(template)
        file_name_index = 0

        with open(f'./uploads/{file_name}', 'r', encoding=UTF_8) as read_obj:
            content_csv_reader = reader(read_obj)
            for row_idx, row in enumerate(content_csv_reader):
                video_file_name = row[file_name_index]
                if row_idx != 0:
                    final_clip = video_builder.get_video_clip(row[1:])
                    final_clip.write_videofile(
                        f'./{BUILDS_DIR}/{video_file_name}.{MP4}', fps=DEFAULT_FPS, codec=LIBX264)
        return 'Success'

    def create_video_file(self, template, content, file_name):
        '''
        create video file from content
        '''
        video_builder = VideoBuilder(template)
        final_clip = video_builder.get_video_clip(content)
        final_clip.write_videofile(
            f'./{BUILDS_DIR}/{file_name}.{MP4}', fps=DEFAULT_FPS, codec=LIBX264)

    def preview_video_file(self, template, content):
        '''
        preview video file from content
        '''
        video_builder = VideoBuilder(template)
        final_clip = video_builder.get_video_clip(content)
        final_clip.resize(height=540).preview()
