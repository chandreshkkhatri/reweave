import unittest
import asyncio
from bson.objectid import ObjectId
from fast_api_app.controllers.video_requests import video_request_model
from src.services.video_builder.moviepy.creator import VideoCreator
from src.commons.enums.templates import VideoTemplates
from commons.config.video_templates import videoTemplates
test_template = 'TEST_TEMPLATE'
global_content = asyncio.run(video_request_model.get_by_id(id=ObjectId('6398b6cba2566bbe19a54553')))
test_content =global_content.get('clips')
# test_content = [{
#     "type": "cover_clip",
#     "image_file_name": "cover.jpg",
# }]

class TestVideoBuilderHelper(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.video_creator = VideoCreator()

    def test_get_video_clip(self):
        self.video_creator.create_video_file(test_template,test_content, 'test')
        pass

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestVideoBuilderHelper('test_get_video_clip'))
    runner = unittest.TextTestRunner()
    runner.run(suite)