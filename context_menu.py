import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
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

    def __init__(self, **kwargs):
        super(ContextMenu, self).__init__(**kwargs)
        self.clock_event = None
        self.orig_parent = None

    def add_obj(self, widget, sub_menu=None):
        self.add_widget(widget)

    def add_item(self, text, sub_menu=None, on_release=None):
        item = ContextMenuTextItem(text)
        if on_release:
            item.bind(on_release=on_release)
        self.add_obj(item, sub_menu=sub_menu)

    def hide(self):
        if not self.parent:
            return

        self.orig_parent = self.parent
        self.parent.remove_widget(self)
        # self.disabled = True
        # self.opacity = 0.0
        # self.y = -100000
        # self.visible = False
        if self.clock_event:
            self.clock_event.cancel()

    def show(self, x=None, y=None):
        if not self.parent:
            self.orig_parent.add_widget(self)
            self.orig_parent = None

            self.hide_submenus()
            self.clock_event = Clock.schedule_interval(partial(self._check_mouse_hover), 0.05)

        if x is not None and y is not None:
            pox_x = x if x + self.width < self.parent.width else x - self.width
            pos_y = y if y - self.height < 0 else y - self.height
            parent_pos = self.parent.pos
            self.pos = (pox_x + parent_pos[0], pos_y + parent_pos[1])


    def _check_mouse_hover(self, obj):
        point = self.to_local(*Window.mouse_pos)
        for widget in self.menu_item_widgets:
            widget.hovered = bool(widget.collide_point(*point))

    def get_height(self):
        height = 0
        for widget in self.children:
            height += widget.height
        return height

    def get_max_width(self):
        max_width = 0
        for widget in self.menu_item_widgets:
            width = widget.label.texture_size[0]
            if width > max_width:
                max_width = width

        return max_width

    def hide_submenus(self):
        for widget in self.menu_item_widgets:
            widget.hide_submenu()

    @property
    def visible(self):
        return bool(self.parent)

    @property
    def menu_item_widgets(self):
        return [w for w in self.children if issubclass(w.__class__, ContextMenuItem)]


class ContextMenuItem:
    hovered = kp.BooleanProperty(False)
    # append_suffix = kp.BooleanProperty(False)
    # item_height = kp.NumericProperty(20)

    # def on_append_suffix(self):
    #     if self.text[-len(self.submenu_postfix):] != self.submenu_postfix:
    #         self.text += self.submenu_postfix

    def __init__(self, **kwargs):
        pass
        # super(ContextMenuItem, self).__init__(**kwargs)

    def get_submenu(self):
        for widget in self.children:
            if issubclass(widget.__class__, ContextMenu):
                return widget
        return None

    def show_submenu(self):
        submenu = self.get_submenu()
        if submenu:
            submenu.show()

    def hide_submenu(self):
        submenu = self.get_submenu()
        if submenu:
            submenu.hide()


class ContextMenuTextItem(ButtonBehavior, FloatLayout, ContextMenuItem):
    submenu_postfix = kp.StringProperty(' ...')
    text = kp.StringProperty('')

    def __init__(self, text=None, **kwargs):
        super(ContextMenuTextItem, self).__init__(**kwargs)
        if text:
            self.label.text = text

    def on_release(self):
        self.parent.hide()

    # def on_text(self, obj, new_text):
        # super(ContextMenuTextItem, self).on_text(*args)
        # self.label.text = new_text
        # if self.text[-len(self.submenu_postfix):] != self.submenu_postfix and \
        #         len([w for w in self.children if issubclass(w.__class__, ContextMenu)]) > 0:
        #     # has sub menu
        #     # print(self, self.text)
        #     self.text += self.submenu_postfix


_path = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(os.path.join(_path, 'context_menu.kv'))
