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
FloatLayout:
    RelativeLayout:
        DesktopVideoPlayer:
            source: "lq_video.mp4"
    Label:
        pos: 0, self.parent.height - 40
        padding: 10, 10
        text: "Hello, world!"
        size_hint: None, None
        size: self.texture_size
"""


class SimplePlayerApp(App):
    def build(self):
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        self.title = 'DesktopVideoPlayer'
        return Builder.load_string(kv)


if __name__ == '__main__':
    SimplePlayerApp().run()
