import kivy
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder

Config.set('graphics', 'width', 800)
Config.set('graphics', 'height', 400)

kivy.require('1.9.0')

from kivy.garden.desktopvideoplayer import DesktopVideoPlayer
# from desktop_video_player import DesktopVideoPlayer

kv = """
DesktopVideoPlayer:
    source: "lq_video.mp4"
"""


class SimplePlayerApp(App):
    def build(self):
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        self.title = 'DesktopVideoPlayer'
        return Builder.load_string(kv)


if __name__ == '__main__':
    SimplePlayerApp().run()
