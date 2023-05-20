import unittest
from microservices.rendering_services.video_builder import video_builder_controller
test_template = 'TEST_TEMPLATE'
test_content = [{
    "type": "cover_clip",
    "image_file_name": "cover1.png",
}]


class TestVideoBuilderHelper(unittest.TestCase):

    def test_get_video_clip(self):
        video_builder_controller.preview_video_file(test_template, test_content)
        pass
