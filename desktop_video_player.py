import kivy
from kivy.uix.relativelayout import RelativeLayout
from kivy.logger import Logger
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.clock import Clock
from functools import partial
import kivy.properties as kp

import os


_path = os.path.dirname(os.path.realpath(__file__))

class DesktopVideoPlayer(RelativeLayout):

    _video = kp.ObjectProperty(None)
    _volume_slider = kp.ObjectProperty(None)
    volume_btn = kp.ObjectProperty(None)

    remaining_label = kp.ObjectProperty(None)
    play_btn = kp.ObjectProperty(None)
    bottom_layout = kp.ObjectProperty(None)

    mouse_hover = kp.BooleanProperty(False)
    # path = kp.StringProperty(_path)
    current_play_btn_image = kp.StringProperty('atlas://data/images/defaulttheme/button')

    current_volume_btn_image = kp.StringProperty('atlas://data/images/defaulttheme/button')

    # state = kp.OptionProperty('stop', options=('play', 'pause', 'stop'))

    source = kp.StringProperty('')

    auto_play = kp.BooleanProperty(True)

    show_elapsed_time = kp.BooleanProperty(True)

    volume_muted = kp.BooleanProperty(False)

    # last_file_selected = StringProperty('')

    def __init__(self, **kwargs):
        super(DesktopVideoPlayer, self).__init__(**kwargs)

        self._update_play_btn_image()
        self._update_volume_btn_image()


        Clock.schedule_interval(partial(self.check_mouse_hover), 0.1)

        # self.video.bind(duration=self.setter('duration'),
        #                 position=self.setter('position'),
        #                 volume=self.setter('volume'),
        #                 source=self.setter('source'),
        #                 state=self.setter('state'))


    def loaded(self):
        if self._video.duration != -1:
            Logger.info('Loaded %s, duration %d', self._video.source, self._video.duration)
            # self._video.seek(0)
            self.ids.progress_bar.max = self._video.duration
            if self._video.duration != 1:
                self._video.y = 0
            if self.auto_play:
                self._video.state = 'play'

    def update_progress(self, val):
        self._update_remaining_time()
        self.ids.progress_bar.value = val

    def _update_remaining_time(self):
        duration = self._video.duration
        progress = self._video.position
        if self.show_elapsed_time:
            self.remaining_label.text = self.sec_to_time_str(progress, force_hours=duration > 3600)
        else:
            self.remaining_label.text = '-' + self.sec_to_time_str(duration - progress, force_hours=duration > 3600)

    def sec_to_time_str(self, sec, force_hours=False):
        hours = int(sec / 3600) if sec >= 3600 else 0
        minutes = int((sec - (hours * 3600)) / 60)
        seconds = int(sec - hours * 3600 - minutes * 60)

        return '%02d:%02d:%02d' % (hours, minutes, seconds) if force_hours or hours > 0 else '%02d:%02d' % (minutes, seconds)

    def seek(self, instance, pos):
        self._video.seek = pos

    def toggle_video(self):
        if self._video.state == 'play':
            self._video.state = 'pause'
        else:
            self._video.state = 'play'


    def video_state_changed(self):
        # print(self._video.state)
        self._update_play_btn_image()

    def check_mouse_hover(self, dt):
        p = self._mouse_pos_to_widget_relative(Window.mouse_pos)
        # print(p, self.x, self.right, self.y, self.top)
        # print(p, self.x, self.y, self.right, self.top)
        if (0 < p[0] - 1 and p[0] + 1 < self.width) and (0 < p[1] - 2 and p[1] < self.height):
            self.bottom_layout.opacity = 1
            self.mouse_hover = True
        else:
            self.bottom_layout.opacity = 0
            self.mouse_hover = False

        # print(self.pos, self._volume_btn.pos)
        # @todo: This is weird, mouse position and widget position aren't relative to this widget
        # if self._volume_btn.x <= p[0] - self.pos[0] <= self._volume_btn.right and self._volume_btn.y <= p[1] - self.pos[1] <= self._volume_btn.top:
        if self._volume_btn.collide_point(*p):
            self._volume_slider.opacity = 1
        elif not self._volume_btn.collide_point(*p) and not self._volume_slider.collide_point(*p):
            self._volume_slider.opacity = 0

    def toggle_remaining_time(self, label_obj):
        self.show_elapsed_time = False if self.show_elapsed_time else True
        self._update_remaining_time()

    def on_source(self, obj, value):
        self._video.source = value.encode('utf8')

    def _get_play_image(self):
        return os.path.join(_path, ("imgs/play.png" if self._video is None or (self._video and (self._video.state == 'pause' or self._video.state == 'stop')) else "imgs/pause.png"))

    def _get_volume_image(self):
        if not self._video:
            return os.path.join(_path, "imgs/volume_on.png")

        if self._video.volume == 0.0:
            return os.path.join(_path, "imgs/volume_off.png")
        if self._volume_slider.value_normalized > 0.5:
            return os.path.join(_path, "imgs/volume_on.png")
        else:
            return os.path.join(_path, "imgs/volume_on_50.png")

    def _update_play_btn_image(self):
        self.current_play_btn_image = self._get_play_image()

    def _update_volume_btn_image(self):
        self.current_volume_btn_image = self._get_volume_image()

    def toggle_muted(self):
        self.volume_muted = True if not self.volume_muted else False
        if self.volume_muted:
            self._video.volume = 0
        else:
            self._video.volume = self._volume_slider.value_normalized
        self._update_volume_btn_image()

    @property
    def volume(self):
        return self._video.volume

    @volume.setter
    def volume(self, value):
        self._video.volume = value
        self._update_volume_btn_image()

    def _mouse_pos_to_widget_relative(self, pos):
        return pos[0] - self.pos[0], pos[1] - self.pos[1]

    # def on_mouse_over(self):
    #     print(".dispatch('on_mouse_over')")
    #     pass
    #
    # def on_mouse_out(self):
    #     pass

#
# class CustomVideoPlayerProgressBar(VideoPlayerProgressBar):
#     def _update_bubble(self, *l):
#         seek = self.seek
#         if self.seek is None:
#             if self.video.duration == 0:
#                 seek = 0
#             else:
#                 seek = self.video.position / self.video.duration
#         # convert to minutes:seconds
#         d = self.video.duration * seek
#         minutes = int(d / 60)
#         seconds = int(d - (minutes * 60))
#         # fix bubble label & position
#         self.bubble_label.text = '%d:%02d' % (minutes, seconds)
#         self.bubble.center_x = self.x + seek * self.width
#         self.bubble.y = self.top / 2 + 5

Builder.load_file(os.path.join(_path, 'desktop_video_player.kv'))
# Factory.register('DesktopVideoPlayer', cls=DesktopVideoPlayer)
# Factory.register('CustomVideoPlayerProgressBar', cls=CustomVideoPlayerProgressBar)
