import kivy
from kivy.app import App
from kivy.lang import Builder
kivy.require('1.9.0')

from kivy.garden.desktopvideoplayer import DesktopVideoPlayer


kv = """
DesktopVideoPlayer:
    source: "DOOM - E3 Teaser Trailer-f3UpX1CMEMQ.mp4"
"""

class SimplePlayerApp(App):
    def build(self):
        return Builder.load_string(kv)


if __name__ == '__main__':
    SimplePlayerApp().run()