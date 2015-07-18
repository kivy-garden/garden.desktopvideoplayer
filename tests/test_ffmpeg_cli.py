import unittest
import os
from ffmpeg_cli import FFmpegCLI


_path = os.path.dirname(os.path.realpath(__file__))

class FFmpegCLITestCase(unittest.TestCase):

    def setUp(self):
        self.test_img1_path = os.path.join(_path, 'mq_video-short-doom-4.jpg')
        self.test_video1_path = os.path.join(_path, 'mq_video-short-doom-4.mp4')
        self.cli = FFmpegCLI()

    def test_is_available(self):
        self.cli.is_available(lambda result: self.assertTrue(result))

    def test_version(self):
        self.cli.version(lambda code,out,err: self.assertEqual(code, 0))

    def test_take_screenshot(self):
        if os.path.exists(self.test_img1_path):
            os.remove(self.test_img1_path)

        def _assert_screenshot_taken( code, out, err):
            self.assertTrue(code == 0)
            self.assertTrue(os.path.exists(self.test_img1_path))
            os.remove(self.test_img1_path)

        self.cli.take_screenshot(self.test_video1_path, 5, self.test_img1_path, _assert_screenshot_taken)

    def test_ffprobe_get_info(self):
        def _assert_get_info(code, out, err):
            self.assertTrue(code == 0)
            print(out)

        self.cli.get_info(self.test_video1_path, _assert_get_info)


if __name__ == "__main__":
    unittest.main()