import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.logger import Logger

Config.set('graphics', 'width', 800)
Config.set('graphics','height', 400)

from kivy.core.window import Window
kivy.require('1.9.0')
# Logger.setLevel('DEBUG')


from kivy.garden.desktopvideoplayer import DesktopVideoPlayer


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
        Config.set('input','mouse', 'mouse,disable_multitouch')
        Window.bind(on_filedrop=self.file_drop)
        self.title = 'DesktopVideoPlayer'
        return Builder.load_string(kv)

    def file_drop(self, filename, *args):
        print(filename)

if __name__ == '__main__':
    SimplePlayerApp().run()
