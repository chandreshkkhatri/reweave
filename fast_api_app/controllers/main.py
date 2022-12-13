"""
Main Controller until the controllers are split into separate files
"""
import sys
from commons.config import *
from bson.objectid import ObjectId

sys.path.append(RESOURCES_DIR)

from src.services.video_builder.moviepy.creator import VideoCreator
from src.services.youtube_interface.request_methods import YouTubeClient
from src.services.text_to_speech import pytts
from fast_api_app.controllers.video_requests import video_request_model
global_content = video_request_model.get_by_id(id=ObjectId('6389eb4aa70b71cd6b063715'))


def one_click_generate_and_upload():
    create_video_file()
    youtube_client = YouTubeClient()
    youtube_client.upload_video(file_name=global_content.get(
        'fileName')+'.mp4', title='Sanskriti Test3')


def create_video_file():
    creator = VideoCreator()
    creator.create_video_file(
        global_content.get('template'),
        content=global_content.get('clips'),
        file_name=global_content.get('fileName'),
    )


def upload_video():
    youtube_client = YouTubeClient()
    youtube_client.upload_video(file_name=global_content.get(
        'fileName')+'.mp4', title='Bajaj HIL')


def preview_video_file():
    creator = VideoCreator()
    creator.preview_video_file(
        global_content.get('template'),
        content=global_content.get('clips'),
    )


def upload_video_with_retries():
    tries = 0
    try:
        tries += 1
        upload_video()
    except Exception as err:
        if tries < 3:
            upload_video()
        else:
            print("Failed to upload video. Error: ", err)


def save_audio():
    pytts.save_audio("Hello, this is a test", "test.mp3")
    