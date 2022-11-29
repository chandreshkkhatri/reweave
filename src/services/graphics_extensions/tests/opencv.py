import unittest

from src.services.graphics_extensions.opencv import main

class TestOpenCVGraphics(unittest.TestCase):
    
    def test_main(self):
        main.main()
        pass

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestOpenCVGraphics('test_main'))
    runner = unittest.TextTestRunner()
    runner.run(suite)