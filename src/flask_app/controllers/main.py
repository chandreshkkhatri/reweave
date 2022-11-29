"""
Main Controller until the controllers are split into separate files
"""

from src.services.video_builder.moviepy.creator import VideoCreator
from src.services.youtube_interface.request_methods import YouTubeClient
from src.services.text_to_speech import pytts
from res.content import content as global_content


def one_click_generate_and_upload():
    create_video_file()
    youtube_client = YouTubeClient()
    youtube_client.upload_video(file_name=global_content.get(
        'file_name')+'.mp4', title='Sanskriti Test3')


def create_video_file():
    creator = VideoCreator()
    creator.create_video_file(
        global_content.get('template'),
        content=global_content.get('content'),
        file_name=global_content.get('file_name'),
    )


def upload_video():
    youtube_client = YouTubeClient()
    youtube_client.upload_video(file_name=global_content.get(
        'file_name')+'.mp4', title='Bajaj HIL')


def preview_video_file():
    creator = VideoCreator()
    creator.preview_video_file(
        global_content.get('template'),
        content=global_content.get('content'),
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
