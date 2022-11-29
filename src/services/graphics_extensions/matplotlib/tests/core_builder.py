import unittest
import logging

from src.services.graphics_extensions.matplotlib.core_builder import CoreBuilder

class TestMatplotlibGraphics(unittest.TestCase):
    def test_builder(self):
        cb = CoreBuilder()
        cb.test()

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestMatplotlibGraphics('test_builder'))
    runner = unittest.TextTestRunner()
    runner.run(suite)