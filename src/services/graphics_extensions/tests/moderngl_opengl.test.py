import unittest

from src.services.graphics_extensions import moderngl

class TestModernGLGraphics(unittest.TestCase):
    def test_create_context(self):
        moderngl.create_context()
        pass

if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(TestModernGLGraphics('test_create_context'))
    runner = unittest.TextTestRunner()
    runner.run(suite)