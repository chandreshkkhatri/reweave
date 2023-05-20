import unittest
from microservices.rendering_services.graphics_extensions.matplotlib.core_builder import CoreBuilder

class TestMatplotlibGraphics(unittest.TestCase):
    def test_builder(self):
        cb = CoreBuilder()
        cb.test()
