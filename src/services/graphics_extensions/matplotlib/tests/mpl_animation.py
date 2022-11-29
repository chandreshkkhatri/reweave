import unittest
import logging

from src.services.graphics_extensions.matplotlib.mpl_animation import MPLAnimation

class TestMatplotlibGraphics(unittest.TestCase):
    def test_animator(self):
        mpl_anime = MPLAnimation()
        mpl_anime.test()

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestMatplotlibGraphics('test_animator'))
    runner = unittest.TextTestRunner()
    runner.run(suite)