import unittest

from desktop_video_player import DesktopVideoPlayer

class DesktopVideoPlayerTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_sec_to_time_str(self):
        player = DesktopVideoPlayer()
        self.assertEqual(player.sec_to_time_str(42), '00:42')
        self.assertEqual(player.sec_to_time_str(69), '01:09')
        self.assertEqual(player.sec_to_time_str(666), '11:06')
        self.assertEqual(player.sec_to_time_str(3600), '01:00:00')
        self.assertEqual(player.sec_to_time_str(4269), '01:11:09')

        # test forced hours
        self.assertEqual(player.sec_to_time_str(666, force_hours=True), '00:11:06')

        # test forced decimal numbers
        self.assertEqual(player.sec_to_time_str(666.321, force_decimals=True, force_hours=True), '00:11:06.321')


if __name__ == "__main__":
    unittest.main()