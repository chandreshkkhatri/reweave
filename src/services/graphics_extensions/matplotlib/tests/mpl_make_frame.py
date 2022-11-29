import unittest

from src.services.graphics_extensions.matplotlib.mpl_make_frame import MPLMakeFrame

class TestMatplotlibGraphics(unittest.TestCase):
    def test_make_frame(self):
        mpl_mf = MPLMakeFrame()
        mpl_mf.test()

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestMatplotlibGraphics('test_make_frame'))
    runner = unittest.TextTestRunner()
    runner.run(suite)