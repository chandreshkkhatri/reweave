import unittest
import sys
sys.path.append('......')

from app.services.rendering_services.graphics_extensions.opencv import main

class TestOpenCVGraphics(unittest.TestCase):
    
    def test_main(self):
        main.main()
        pass
