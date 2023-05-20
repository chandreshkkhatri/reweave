import unittest

from microservices.rendering_services.graphics_extensions.matplotlib.mpl_animation import MPLAnimation

class TestMatplotlibGraphics(unittest.TestCase):
    def test_animator(self):
        mpl_anime = MPLAnimation()
        mpl_anime.test()
