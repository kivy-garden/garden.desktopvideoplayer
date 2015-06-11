import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from functools import partial
import kivy.properties as kp
import os



class ContextMenu(GridLayout):

    # item_height = kp.NumericProperty(30)

    def __init__(self, **kwargs):
        super(ContextMenu, self).__init__(**kwargs)
        self.clock_event = None

    def add_obj(self, widget, sub_menu=None):
        self.add_widget(widget)

    def add_item(self, text, sub_menu=None, on_release=None):
        if sub_menu:
            text += ' ...'

        item = ContextMenuTextItem(text)
        if on_release:
            item.bind(on_release=on_release)
        self.add_obj(item, sub_menu=sub_menu)

    def hide(self):
        self.disabled = True
        self.opacity = 0.0
        self.y = -100000
        # self.visible = False
        if self.clock_event:
            self.clock_event.cancel()

    def show(self, x=None, y=None):
        self._resize_text_sizes()

        self.width = self._get_max_width()
        self.height = self._get_height()

        print(self.width, self.height)

        if x is not None and y is not None:
            pox_x = x if x + self.width < self.parent.width else x - self.width
            pos_y = y if y - self.height < 0 else y - self.height
            parent_pos = self.parent.pos
            self.pos = (pox_x + parent_pos[0], pos_y + parent_pos[1])

        self.opacity = 1.0
        self.disabled = False

        # self._get_height()
        # self.visible = True

        self.clock_event = Clock.schedule_interval(partial(self._check_mouse_hover), 0.05)

    # def on_disabled(self, obj, value):
    #     if self.disabled:
    #         self.hide()
    #     else:
    #         self.show()

    # def on_item_released(self, obj):
    #     print('aa')

    def _check_mouse_hover(self, obj):
        point = self.to_local(*Window.mouse_pos)
        for widget in self.children:
            if issubclass(widget.__class__, ContextMenuItem):
                widget.hovered = bool(widget.collide_point(*point))

    def _get_height(self):
        height = 0
        for widget in self.children:
            height += widget.height
        return height

    def _get_max_width(self):
        max_width = 0
        for widget in self.children:
            if issubclass(widget.__class__, ContextMenuItem):
                width = widget.texture_size[0]
                if width > max_width:
                    max_width = width

        return max_width

    def _resize_text_sizes(self):
        width = self._get_max_width()
        for widget in self.children:
            if issubclass(widget.__class__, ContextMenuItem):
                widget.text_size = width, widget.height
                widget.width = width


class ContextMenuItem:
    hovered = kp.BooleanProperty(False)
    # item_height = kp.NumericProperty(20)

    def __init__(self, **kwargs):
        pass
        # super(ContextMenuItem, self).__init__(**kwargs)


class ContextMenuTextItem(ButtonBehavior, Label, ContextMenuItem):

    def __init__(self, text=None, **kwargs):
        super(ContextMenuTextItem, self).__init__(**kwargs)
        if text:
            self.text = text

    def on_release(self):
        self.parent.hide()


_path = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(os.path.join(_path, 'context_menu.kv'))
