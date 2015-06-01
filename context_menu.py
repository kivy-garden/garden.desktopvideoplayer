import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
import os


class ContextMenu(GridLayout):

    def add_item(self, text):
        item = ContextMenuItem(text)
        self.add_widget(item)


    def visible(self):
        return not self.disabled

    def hide(self):
        self.disabled = True
        self.opacity = 0.0
        self.y = -1000

    def show(self, x=None, y=None):
        self.width = self.children[0].size[0]

        if x is not None and y is not None:
            self.pos = \
                (x if x + self.width < self.parent.width else x - self.width, y if y - self.height < 0 else y - self.height)

        self.disabled = False
        self.opacity = 1.0

class ContextMenuItem(ButtonBehavior, Label):
    def __init__(self, text, **kwargs):
        super(ContextMenuItem, self).__init__(**kwargs)
        # print(self.on_release)
        # self.bind(on_press=self.on_press)

        # self.on_release = kwargs['on_release']

        self.text = text

    def on_release(self):
        print('on_release')

_path = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(os.path.join(_path, 'context_menu.kv'))
