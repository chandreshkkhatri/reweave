"""
Main Controller until the controllers are split into separate files
"""
import sys
import asyncio
from commons.config import config
from bson.objectid import ObjectId

sys.path.append(config.RESOURCES_DIR)

from microservices.rendering_services.video_builder import video_builder_controller
from microservices.youtube_interface.request_methods import YouTubeClient
from microservices.rendering_services.text_to_speech import pytts
from server_modules.model import video_request_model
global_content = {
    'template': 'NIFTY500',
    'clips': [
        {
            'type': 'text',
            'text': 'Hello World',
            'duration': 5,
            'image_file_name': 'cover1.png'
        },
    ],
    'fileName': 'test',
}


def one_click_generate_and_upload():
    create_video_file()
    youtube_client = YouTubeClient()
    youtube_client.upload_video(file_name=global_content.get(
        'fileName')+'.mp4', title='Sanskriti Test3')


async def create_video_file():
    await video_builder_controller.create_video_file(
        global_content.get('template'),
        content=global_content.get('clips'),
        file_name=global_content.get('fileName'),
    )


def upload_video():
    youtube_client = YouTubeClient()
    youtube_client.upload_video(file_name=global_content.get(
        'fileName')+'.mp4', title='Bajaj HIL')


def preview_video_file():
    video_builder_controller.preview_video_file(
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
    