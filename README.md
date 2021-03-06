# DesktopVideoPlayer

Alternative video player designed to work well with desktop applications.

![Minimal implementation of DesktopVideoPlayer](https://raw.githubusercontent.com/kivy-garden/garden.desktopvideoplayer/master/doc/simple_player.png)

## Features

- Based on the default [uix.video](http://kivy.org/docs/api-kivy.uix.video.html) component
- Controls (including volume) show on mouse hover
- Togglable time label with elapsed/remaining times
- Play/pause on mouse click or space bar pressed
- Context menu on right mouse click
- (planned) `ffmpeg` integration to capture screenshots
- (planned) Detailed information about the video
- Precise jump to location set by hh:mm:ss
- (planned) Bubble showing when hovering over the progress bar
- (planned) Simple playlist functionality

## Installation

Install from [Kivy garden](http://kivy-garden.github.io/) with:

    garden install desktopvideoplayer

## Demo

Package contains minimal demo project. You can run it from installed kivy garden package directory:

    kivy examples/simple_player.py 
    
## Usage

DesktopVideoPlayer behaves just like the default video player (work in progress).

```python
import kivy
from kivy.app import App
from kivy.lang import Builder
kivy.require('1.9.0')

from kivy.garden.desktopvideoplayer import DesktopVideoPlayer

kv = """
DesktopVideoPlayer:
    source: "path/to/my/video"
"""

class SimplePlayerApp(App):
    def build(self):
        return Builder.load_string(kv)

if __name__ == '__main__':
    SimplePlayerApp().run()
```

# Tests

Testing FFmpeg wrapper:

```kivy tests/test_ffmpeg_cli.py```



# License

DesktopVideoPlayer is licensed under MIT license.

Video used in the `simple_player.py` example app and on the screenshot is from [Construct GTC Teaser Trailer](https://www.youtube.com/watch?v=8JItUtHwKiE).

Icons used in this player are based on [http://www.freebiesgallery.com/video-player-psd/](http://www.freebiesgallery.com/video-player-psd/).