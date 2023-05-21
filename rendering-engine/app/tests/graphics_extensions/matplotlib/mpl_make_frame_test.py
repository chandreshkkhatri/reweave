import unittest

from app.services.rendering_services.graphics_extensions.matplotlib.mpl_make_frame import MPLMakeFrame

class TestMatplotlibGraphics(unittest.TestCase):
    def test_make_frame(self):
        mpl_mf = MPLMakeFrame()
        mpl_mf.test()
