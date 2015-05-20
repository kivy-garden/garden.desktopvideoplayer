import kivy
from kivy.uix.relativelayout import RelativeLayout
from kivy.logger import Logger
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.clock import Clock
from functools import partial
import kivy.properties as kp

import os


_path = os.path.dirname(os.path.realpath(__file__))

class DesktopVideoPlayer(RelativeLayout):

    video = kp.ObjectProperty(None)
    remaining_label = kp.ObjectProperty(None)
    play_btn = kp.ObjectProperty(None)
    mouse_hover = kp.BooleanProperty(False)
    # path = kp.StringProperty(_path)
    current_play_btn_image = kp.StringProperty(None)
    current_play_btn_down_image = kp.StringProperty(None)

    # last_file_selected = StringProperty('')

    def __init__(self, **kwargs):
        super(DesktopVideoPlayer, self).__init__(**kwargs)

        self.video_pause_position = 0.0
        # self.video = self.ids.wg_video

        self.current_play_btn_image = self._get_play_image()

        # self.bind(current_play_btn_image=)

        # self.video.y = -1000
        # self.runtime_config = kwargs['runtime_config'] if 'runtime_config' in kwargs.keys() else None

        # Window.bind(on_motion=self.mouse_move)
        Clock.schedule_interval(partial(self.check_mouse_hover), 0.1)

    # def init(self):
    #     print('init')

        # self.video.bind(loaded=self.show_video)
        # self.video.bind(position=self.update_progress_bar)

    # def open_file_chooser(self):
    #     content = video_chooser.VideoChooser(load=self.load, cancel=self.dismiss_popup, default_dir=self.default_dir())
    #     self._popup = Popup(title="Save file", content=content, size_hint=(0.9, 0.9))
    #     self._popup.open()

    # def dismiss_popup(self):
    #     self._popup.dismiss()


    def load(self, filename):
        # print(path)
        # print(filename)
        # filename = filename[0]
        # self.video_orig_parent.add_widget(self.video)

        self.video.source = filename
        # self.video.state = 'play'

        # if self.runtime_config:
        #     self.runtime_config.set('recent_dir', os.path.dirname(os.path.abspath(filename)))

        # self.dismiss_popup()

    def loaded(self):
        # print(self.video.duration)
        if self.video.duration != -1:
            Logger.info('Loaded %s, duration %d', self.video.source, self.video.duration)
            self.video.seek(0)
            self.video.state = 'play'
            self.ids.progress_bar.max = self.video.duration
        # if self.video.state == 'play':
            self.video.y = 0
            # self.current_play_btn_image = self._get_play_image()
            # self.play_btn.dispatch('background_normal')


    def update_progress(self, val):
        # d = self.video.duration * val
        self.remaining_label.text = self.sec_to_time_str(val, force_hours=self.video.duration > 3600)

        self.ids.progress_bar.value = val

    def sec_to_time_str(self, sec, force_hours=False):
        hours = int(sec / 3600) if sec >= 3600 else 0
        minutes = int((sec - (hours * 3600)) / 60)
        seconds = int(sec - hours * 3600 - minutes * 60)

        return '%02d:%02d:%02d' % (hours, minutes, seconds) if force_hours or hours > 0 else '%02d:%02d' % (minutes, seconds)

    # def default_dir(self):
    #     def_dir = self.runtime_config.get('recent_dir')
    #     return def_dir if def_dir else os.path.expanduser("~")

    def seek(self, instance, pos):
        self.video.seek = pos

    def toggle_video(self):
        if self.video.state == 'play':
            self.video_pause_position = self.video.position
            self.video.state = 'pause'
        else:
            self.video.position = self.video_pause_position
            self.video.state = 'play'


    def video_state_changed(self):
        print(self.video.position)
        self.current_play_btn_image = self._get_play_image()
        # self.video.position = self.video_pause_position
        # self.video.position = self.video_pause_position

    def check_mouse_hover(self, dt):

        p = Window.mouse_pos
        if self.collide_point(p[0], p[1]) and p[0] > 1 and p[1] > 1 and Window.width:
            # self.ids.top_layout.opacity = 1
            # self.dispatch('on_mouse_over')
            self.ids.bottom_layout.opacity = 1
            self.mouse_hover = True
        else:
            # self.dispatch('on_mouse_out')
            # self.ids.top_layout.opacity = 0
            self.ids.bottom_layout.opacity = 0
            self.mouse_hover = False

    def toggle_remaining_time(self, label_obj):
        print(label_obj.texture_size)
        pass


    def _get_play_image(self):
        return _path + ("/imgs/play.png" if self.video is None or (self.video and self.video.state == 'pause') else "/imgs/pause.png")


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
