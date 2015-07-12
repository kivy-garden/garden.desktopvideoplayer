import kivy
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.relativelayout import FloatLayout
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.clock import Clock
from functools import partial
from ffmpeg_cli import FFmpegCLI
import context_menu
import kivy.properties as kp
import os


_path = os.path.dirname(os.path.realpath(__file__))


class DesktopVideoPlayer(FloatLayout):

    _video = kp.ObjectProperty(None)
    _volume_slider = kp.ObjectProperty(None)
    _volume_btn = kp.ObjectProperty(None)
    context_menu = kp.ObjectProperty(None)

    remaining_label = kp.ObjectProperty(None)
    play_btn = kp.ObjectProperty(None)
    bottom_layout = kp.ObjectProperty(None)

    # path = kp.StringProperty(_path)
    current_play_btn_image = kp.StringProperty('atlas://data/images/defaulttheme/button')
    current_volume_btn_image = kp.StringProperty('atlas://data/images/defaulttheme/button')

    source = kp.StringProperty('')

    mouse_hover = kp.BooleanProperty(False)
    auto_play = kp.BooleanProperty(True)
    show_elapsed_time = kp.BooleanProperty(True)
    volume_muted = kp.BooleanProperty(False)
    _initialized = kp.BooleanProperty(False)

    # last_file_selected = StringProperty('')

    def __init__(self, *args, **kwargs):
        super(DesktopVideoPlayer, self).__init__(*args, **kwargs)

        # self.register_event_type('on_context_menu_show')
        # self.register_event_type('on_context_menu_hide')

        self.ffmpeg = FFmpegCLI()

        self._update_play_btn_image()
        self._update_volume_btn_image()

        Clock.schedule_interval(partial(self._check_mouse_hover), 0.1)
        Window.bind(on_key_down=self._on_key_down)

        # self.video.bind(duration=self.setter('duration'),
        #                 position=self.setter('position'),
        #                 volume=self.setter('volume'),
        #                 source=self.setter('source'),
        #                 state=self.setter('state'))

    def _init(self, *args):
        self.context_menu.visible = False
        # self.context_menu.add_item("Jump to", on_release=self._context_item_release)
        # self.context_menu.add_item("test long text #2", on_release=self._context_item_release)
        # self.context_menu.add_item("test #3", on_release=self._context_item_release)
        self._initialized = True

    def loaded(self):
        if self._video.duration != -1:
            Logger.info('Loaded %s, duration %d', self._video.source, self._video.duration)
            # self._video.seek(0)
            self.ids.progress_bar.max = self._video.duration
            if self._video.duration != 1:
                self._video.opacity = 1.0
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
        if self._video.duration == -1:
            return

        if self._video.state == 'play':
            self._video.state = 'pause'
        else:
            self._video.state = 'play'

    def video_state_changed(self):
        self._update_play_btn_image()

    def _check_mouse_hover(self, dt):
        p = Window.mouse_pos

        if (self.x < p[0] - 1 and p[0] + 1 < self.right) and (self.y < p[1] - 2 and p[1] < self.top):
            self.bottom_layout.opacity = 1
            self.mouse_hover = True
        else:
            self.bottom_layout.opacity = 0
            self.mouse_hover = False

        # @todo: This is weird, mouse position and widget position aren't relative to this widget
        if self._volume_btn.collide_point(*p):
            self._volume_slider.opacity = 1
            self._volume_slider.disabled = False
            self._volume_slider.y = self._volume_slider.parent.pos[1] + self._volume_slider.parent.height
        elif not self._volume_btn.collide_point(*p) and not self._volume_slider.collide_point(*p):
            self._volume_slider.opacity = 0
            self._volume_slider.disabled = True
            self._volume_slider.y = -100000

    def toggle_remaining_time(self, label_obj):
        self.show_elapsed_time = False if self.show_elapsed_time else True
        self._update_remaining_time()

    def on_source(self, obj, value):
        Logger.info('Opening "%s"', value)
        self._video.source = value

    def _on_key_down(self, *args):
        keycode = args[1]
        if keycode == 32:
            self.toggle_video()

    def _on_touch_down(self, obj, click_event):
        if self.collide_point(*click_event.pos):
            if click_event.button == 'left':
                if self.context_menu.visible:
                    self.context_menu.visible = False
                else:
                    self.toggle_video()
            elif click_event.button == 'right':
                p = self._mouse_pos_to_widget_relative(click_event.pos)
                self.context_menu.show(*p)
        else:
            self.context_menu.visible = False

    def _get_play_image(self):
        if self._video is None or (self._video and (self._video.state == 'pause' or self._video.state == 'stop')):
            return os.path.join(_path, "imgs/play.png")
        else:
            return os.path.join(_path, "imgs/pause.png")

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

    def jump_to(self, hours, minutes, seconds):
        total_seconds = hours * 3600 + minutes * 60 + seconds
        if total_seconds > self._video.duration:
            self._video.seek(1)
        else:
            self._video.seek(float(total_seconds) / self._video.duration)
        self.context_menu.visible = False

    def take_screenshot(self, hours, minutes, seconds):
        total_seconds = hours * 3600 + minutes * 60 + seconds

    def save_screenshot_to_desktop(self):
        # print(self._video.position)
        # print(self._video.position - int(self._video.position))
        pass

    def save_screenshot_to_home_dir(self):
        dest = os.path.join(os.path.splitext(self.source)[0], self.sec_to_time_str(int(self._video.position)) + '.jpg')
        self.ffmpeg.take_screenshot(self.source, self._video.position, dest)

    def save_screenshot_to_the_same_dir(self):
        pass


class JumpToMenu(RelativeLayout, context_menu.ContextMenuItem):

    def __init__(self, *args, **kwargs):
        super(JumpToMenu, self).__init__(*args, **kwargs)
        self.register_event_type('on_jump_button_released')

    def on_touch_down(self, click_event):
        super(JumpToMenu, self).on_touch_down(click_event)
        return self.collide_point(click_event.x, click_event.y)

    def get_time_str(self):
        return self.hours_input.text + ':' + self.minutes_input.text + ':' + self.seconds_input.text

    def on_jump_button_released(self, hours, minutes, seconds):
        pass

    def _dispatch_jump_event(self, hours, minutes, seconds):
        def _str_to_int(s):
            try:
                return int(s)
            except ValueError:
                return 0

        hours = abs(_str_to_int(hours))
        minutes = abs(_str_to_int(minutes)) % 60
        seconds = abs(_str_to_int(seconds)) % 60
        self.dispatch('on_jump_button_released', hours, minutes, seconds)


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
