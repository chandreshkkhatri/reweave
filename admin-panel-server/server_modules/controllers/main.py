"""
Main Controller until the controllers are split into separate files
"""
import sys
import asyncio
from commons.config import config
from bson.objectid import ObjectId

sys.path.append(config.RESOURCES_DIR)

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
    pass


async def create_video_file():
    pass


def upload_video():
    pass


def preview_video_file():
    pass


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
    pass
    