import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
import kivy.properties as kp
import os


class ContextMenu(GridLayout):

    visible = kp.BooleanProperty(False)

    def add_item(self, text):
        item = ContextMenuItem(text)
        self.add_widget(item)

    def _hide(self):
        self.disabled = True
        self.opacity = 0.0
        self.y = -100000
        self.visible = False

    def show(self, x=None, y=None):
        # for w in self.children:
        #     print(w.width)
        self._resize_text_sizes()

        self.width = self._get_max_width()

        if x is not None and y is not None:
            pox_x = x if x + self.width < self.parent.width else x - self.width
            pos_y = y if y - self.height < 0 else y - self.height
            parent_pos = self.parent.pos
            self.pos = (pox_x + parent_pos[0], pos_y + parent_pos[1])

        self.disabled = False
        self.opacity = 1.0
        self.visible = True

    def on_visible(self, obj, value):
        if self.visible:
            self.show()
        else:
            self._hide()

    def _get_max_width(self):
        max_width = 0
        for widget in self.children:
            if type(widget) == ContextMenuItem:
                width = widget.texture_size[0]
                if width > max_width:
                    max_width = width

        return max_width

    def _resize_text_sizes(self):
        width = self._get_max_width()
        for widget in self.children:
            if type(widget) == ContextMenuItem:
                widget.text_size = width, widget.height
                widget.width = width

class ContextMenuItem(ButtonBehavior, Label):
    def __init__(self, text, **kwargs):
        super(ContextMenuItem, self).__init__(**kwargs)
        self.text = text

    def on_release(self):
        print(self.text)
        self.parent.visible = False


_path = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(os.path.join(_path, 'context_menu.kv'))
