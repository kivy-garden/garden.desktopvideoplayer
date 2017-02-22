import os
from functools import partial

from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.relativelayout import RelativeLayout

from context_menu import ContextMenuItem, ContextMenuTextItem, ContextMenuHoverableItem
from ffmpeg_cli import FFmpegCLI

_path = os.path.dirname(os.path.realpath(__file__))


class DesktopVideoPlayer(RelativeLayout):

    _video = ObjectProperty(None)
    _notify_bubble = ObjectProperty(None)
    _volume_slider = ObjectProperty(None)
    _volume_btn = ObjectProperty(None)
    _info_box = ObjectProperty(None)

    _show_info_menu_option = ObjectProperty(None)
    _take_screenshot_menu_option = ObjectProperty(None)

    context_menu = ObjectProperty(None)
    # _advanced_options = kp.ObjectProperty(None)

    remaining_label = ObjectProperty(None)
    play_btn = ObjectProperty(None)
    bottom_layout = ObjectProperty(None)

    # path = kp.StringProperty(_path)
    current_play_btn_image = StringProperty('')
    current_volume_btn_image = StringProperty('')

    source = StringProperty('')
    volume = NumericProperty(1.0)

    mouse_hover = BooleanProperty(False)
    auto_play = BooleanProperty(True)
    show_elapsed_time = BooleanProperty(True)
    volume_muted = BooleanProperty(False)
    check_mouse_hover = BooleanProperty(False)

    _initialized = BooleanProperty(False)

    # last_file_selected = StringProperty('')

    def __init__(self, **kwargs):
        super(DesktopVideoPlayer, self).__init__(**kwargs)

        # self.register_event_type('on_context_menu_show')
        # self.register_event_type('on_context_menu_hide')

        self._bubble_anim = None
        self._bubble_timeout = None
        self._mouse_check_timer = None
        self._advanced_options_parent = None
        self._update_play_btn_image()
        self._update_volume_btn_image()

        self.check_mouse_hover = True
        Window.bind(on_key_down=self._on_key_down)

        # self.video.bind(duration=self.setter('duration'),
        #                 position=self.setter('position'),
        #                 volume=self.setter('volume'),
        #                 source=self.setter('source'),
        #                 state=self.setter('state'))

    def _init(self, *args):
        self.context_menu.visible = False
        # self.context_menu.add_item("Jump to", on_release=self._context_item_release)
        self.remove_widget(self._notify_bubble)
        self.remove_widget(self._info_box)

        # self._advanced_options_parent = self._advanced_options.parent
        # self._advanced_options.parent.remove_widget(self._advanced_options)

        self._ffmpeg = FFmpegCLI()
        self._ffmpeg.is_available(lambda result: self._toggle_video_menu_options(result))
        self._initialized = True

    def _toggle_video_menu_options(self, available):
        self._show_info_menu_option.disabled = not available
        self._take_screenshot_menu_option.disabled = not available

    @property
    def context_menu_visible(self):
        return bool(self.context_menu)

    def on_check_mouse_hover(self, obj, new_value):
        if new_value:
            self._mouse_check_timer = Clock.schedule_interval(partial(self._check_mouse_hover), 0.1)
        else:
            self._mouse_check_timer.cancel()

    def show_notify_bubble(self, text, timeout=None):
        if not self._notify_bubble.parent:
            self.add_widget(self._notify_bubble)

        if self._bubble_anim:
            self._bubble_anim.cancel(self._notify_bubble)

        self._notify_bubble.text = text
        self._bubble_anim = Animation(opacity=1.0, duration=0.25)
        self._bubble_anim.start(self._notify_bubble)

        if self._bubble_timeout:
            self._bubble_timeout.cancel()
        if timeout:
            self._bubble_timeout = Clock.schedule_once(partial(self.hide_notify_bubble), timeout)

    def hide_notify_bubble(self, *args):
        def _hide(*args):
            self.remove_widget(self._notify_bubble)
            self._bubble_timeout = None

        self._bubble_anim = Animation(opacity=0.0, duration=0.25)
        self._bubble_anim.bind(on_complete=_hide)
        self._bubble_anim.start(self._notify_bubble)

    def _loaded(self):
        if self._video.duration != -1:
            Logger.info('Loaded %s, duration %d', self._video.source, self._video.duration)
            # self._video.seek(0)
            self.ids.progress_bar.max = self._video.duration
            if self._video.duration != 1:
                self._video.opacity = 1.0
            if self.auto_play:
                self._video.state = 'play'

    def _update_progress(self, val):
        self._update_remaining_time()
        self.ids.progress_bar.value = val

    def _update_remaining_time(self):
        duration = self._video.duration
        progress = self._video.position
        if self.show_elapsed_time:
            self.remaining_label.text = self.sec_to_time_str(progress, force_hours=duration > 3600)
        else:
            self.remaining_label.text = '-' + self.sec_to_time_str(duration - progress, force_hours=duration > 3600)

    def sec_to_time_str(self, sec, force_hours=False, force_decimals=False):
        hours = int(sec / 3600) if sec >= 3600 else 0
        minutes = int((sec - (hours * 3600)) / 60)
        seconds = int(sec - hours * 3600 - minutes * 60)

        time_str = '%02d:%02d:%02d' % (hours, minutes, seconds) if force_hours or hours > 0 else \
            '%02d:%02d' % (minutes, seconds)
        if force_decimals:
            time_str += str(sec - int(sec))[1:]

        return time_str

    def seek(self, instance, pos):
        self._video.seek = pos

    def toggle_video(self):
        """
        Play/Pause video
        """
        if self._video.duration == -1:
            return

        if self._video.state == 'play':
            self._video.state = 'pause'
        else:
            self._video.state = 'play'

    def _video_state_changed(self):
        self._update_play_btn_image()

    def _check_mouse_hover(self, *args):
        widget_pos = self.to_window(0, 0)
        # p = self.to_local(*Window.mouse_pos)
        # print(p, self.pos, self.to_local(*p), self.to_window(*p))
        # print(self.to_window(*p))
        p = Window.mouse_pos[0] - widget_pos[0], Window.mouse_pos[1] - widget_pos[1]
        # print(mouse_pos, p)

        if (self.x < p[0] - 1 and p[0] + 1 < self.right) and (self.y < p[1] - 2 and p[1] < self.top):
        # if self.collide_point(*p):
            self.bottom_layout.opacity = 1
            self.mouse_hover = True
        else:
            self.bottom_layout.opacity = 0
            self.mouse_hover = False

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

    def on_volume(self, obj, new_value):
        self._video.volume = new_value
        self._update_volume_btn_image()

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
        # negate boolean value represented as BooleanProperty
        # @todo: There might be an easier way
        # self.volume_muted = True if not self.volume_muted else False
        self.volume_muted = not bool(self.volume_muted)
        if self.volume_muted:
            self._video.volume = 0
        else:
            self._video.volume = self._volume_slider.value_normalized
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

    def take_screenshot(self, position, dest_dir):
        time_str = self.sec_to_time_str(round(position, 3), force_decimals=True, force_hours=True)
        frames = self._advanced_options.get_frames()
        file_format = self._advanced_options.get_selected_format()
        destination_file = os.path.join(dest_dir, os.path.splitext(os.path.basename(self.source))[0] + '-' +
                                 time_str.replace(':', '-'))
        counter_format = None

        if frames > 1:
            counter_format = '%0' + str(int(frames / 10.0) + 1) + 'd'
            destination_file += '_' + counter_format
        destination_file += '.' + file_format

        Logger.info('Saving screenshot from %s (%d frames) to "%s"', time_str, frames,  destination_file)

        self.show_notify_bubble('Taking screenshot' + ('s' if frames > 1 else '') + ' ...')

        def _show_notify(code, out, err):
            if counter_format:
                human_file_name = destination_file.replace(counter_format, '[0-' + str(frames - 1) + ']')
            else:
                human_file_name = destination_file
            self.show_notify_bubble('Saved to {path}'.format(path=human_file_name), 5)

        self._ffmpeg.take_screenshot(self.source, self._video.position, destination_file, _show_notify, frames=frames)
        self.context_menu.visible = False

    # def save_screenshot_to_desktop(self):
    #     pass

    def save_screenshot_to_home_dir(self):
        self.take_screenshot(self._video.position, os.path.expanduser('~'))

    def save_screenshot_to_the_same_dir(self):
        self.take_screenshot(self._video.position, os.path.dirname(os.path.realpath(self.source)))

    def save_screenshot_to_dir(self, dir):
        if not os.path.exists(dir):
            return
        self.take_screenshot(self._video.position, dir)

    def show_info(self):
        print(self._ffmpeg)

        def _show_info(code, out, err):
            self.show_info_box(err)

        self._ffmpeg.get_info(self.source, _show_info, True)
        self.context_menu.visible = False

    def hide_info_box(self):
        def _hide(*args):
            self.remove_widget(self._info_box)

        self.check_mouse_hover = True
        anim = Animation(opacity=0, duration=0.25)
        anim.bind(on_complete=_hide)
        anim.start(self._info_box)

    def show_info_box(self, text):
        self._info_box.content.text = text
        self.check_mouse_hover = False

        if not self._info_box.parent:
            self.add_widget(self._info_box)

        anim = Animation(opacity=1, duration=0.25)
        anim.start(self._info_box)


class JumpToMenu(ContextMenuHoverableItem):

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
                return int(s.strip())
            except ValueError:
                return 0

        hours = abs(_str_to_int(hours))
        minutes = abs(_str_to_int(minutes)) % 60
        seconds = abs(_str_to_int(seconds)) % 60
        self.dispatch('on_jump_button_released', hours, minutes, seconds)


class TakeScreenshotSaveTo(ContextMenuTextItem):
    def __init__(self, **kwargs):
        super(TakeScreenshotSaveTo, self).__init__(**kwargs)
        self.register_event_type('on_save_released')

    def on_save_released(self, text):
        pass


class AdvancedOptions(ContextMenuItem):
    _format_png_btn = ObjectProperty(None)
    _format_jpg_btn = ObjectProperty(None)
    _frames_input = ObjectProperty(None)

    def on_touch_down(self, click_event):
        super(AdvancedOptions, self).on_touch_down(click_event)
        return self.collide_point(click_event.x, click_event.y)

    def get_selected_format(self):
        if self._format_png_btn.state == 'down':
            return 'png'
        elif self._format_jpg_btn.state == 'down':
            return 'jpg'

    def get_frames(self):
        try:
            return int(self._frames_input.text.strip())
        except:
            return 1

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
