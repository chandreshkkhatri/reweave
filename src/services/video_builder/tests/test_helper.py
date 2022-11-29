import unittest

from src.services.video_builder import VideoBuilder

class TestVideoBuilderHelper(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.video_builder = VideoBuilder(video_template=None)

    def test_get_video_clip(self):
        self.assertEqual(0, 0)
        pass

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestVideoBuilderHelper('test_get_video_clip'))
    runner = unittest.TextTestRunner()
    runner.run(suite)