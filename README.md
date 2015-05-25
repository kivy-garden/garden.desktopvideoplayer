# DesktopVideoPlayer

Alternative video player designed to work well with desktop applications.

![Minimal implementation of DesktopVideoPlayer](https://raw.githubusercontent.com/kivy-garden/garden.desktopvideoplayer/master/doc/simple_player.png)

## Features

- Supports all formats as the default [uix.video](http://kivy.org/docs/api-kivy.uix.video.html) component
- Controls (including volume) show on mouse hover
- Togglable time label with elapsed/remaining times
- Play/pause on mouse click
- (planned) Context menu on right mouse click
- (planned) `ffmpeg` integration to capture screenshots
- (planned) Detailed information about the video
- (planned) Precise jump to location set by hh:mm:ss.frame
- (planned) Bubble showing when hovering over the progress bar
- (planned) Simple playlist functionality

## Installation

Install from [Kivy garden](http://kivy-garden.github.io/) with:

    garden install desktopvideoplayer

## Demo

Package contains minimal demo project. You can run it from your installed kivy package directory:

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

# License

DesktopVideoPlayer is licensed under MIT license.

Icons used in this player are based on [http://www.freebiesgallery.com/video-player-psd/](http://www.freebiesgallery.com/video-player-psd/).