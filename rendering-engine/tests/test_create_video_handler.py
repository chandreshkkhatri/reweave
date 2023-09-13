"""
Test create video handler
"""
import pytest

from app.handlers.create_video_handler import create_video_file, preview_video_file
from app.services.rendering_services.video_builder.core_builder.builder import VideoBuilder


content = [
    {
        "type": "TITLE_CLIP",
        "text": "test",
        "image_file_name": "test",
    },]


@pytest.mark.parametrize(
    "video_builder, expected",
    [
        (VideoBuilder(), True),
        (None, False),
    ],
)
def test_create_video_file(video_builder, expected):
    """
    Test create video file
    """
    file_name = "test"
    assert create_video_file(
        video_builder, content=content, file_name=file_name) == expected


@pytest.mark.parametrize(
    "video_builder, expected",
    [
        (VideoBuilder(), True),
        (None, False),
    ],
)
def test_preview_video_file(video_builder, expected):
    """
    Test preview video file
    """
    assert preview_video_file(
        video_builder, content=content) == expected
