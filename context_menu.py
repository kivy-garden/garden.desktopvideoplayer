import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
# from kivy.uix.relativelayout import RelativeLayout
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

    visible = kp.BooleanProperty(False)
    spacer = kp.ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ContextMenu, self).__init__(*args, **kwargs)
        self.clock_event = None
        self.orig_parent = None
        self._on_visible(False)

    def add_obj(self, widget, sub_menu=None):
        self.add_widget(widget)

    def add_item(self, text, sub_menu=None, on_release=None):
        item = ContextMenuTextItem(text)
        if on_release:
            item.bind(on_release=on_release)
        self.add_obj(item, sub_menu=sub_menu)

    # def hide(self):
    #     self.visible = False

    def show(self, x=None, y=None):
        self.visible = True
        self._add_to_parent()

        context_root_parent = self.parent
        while issubclass(context_root_parent.__class__, ContextMenuItem) \
                or issubclass(context_root_parent.__class__, ContextMenu):
            context_root_parent = context_root_parent.parent

        # context_total_parent = [widget for widget in self.p]

        if x is not None and y is not None:
            pox_x = x if x + self.width < context_root_parent.width else x - self.width
            pos_y = y if y - self.height < 0 else y - self.height
            parent_pos = context_root_parent.pos
            self.pos = (pox_x + parent_pos[0], pos_y + parent_pos[1])
            # print(self.pos)
            # self._set_positions()

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
            width = widget.content_width
            if width > max_width:
                max_width = width

        return max_width

    def hide_submenus(self):
        for widget in self.menu_item_widgets:
            widget.hide_submenu()

    # @property
    # def visible(self):
    #     return bool(self.parent)

    def _on_visible(self, new_visibility):
        if new_visibility:
            self.size = self.get_max_width(), self.get_height()
            # print(self.get_height())
            # self.visible = (self.parent is not None)
            self._add_to_parent()
            # for submenu in self.menu_item_widgets:
            #     submenu.update_arrows()
        elif self.parent and not new_visibility:
            self.orig_parent = self.parent
            # self.parent.submenu = self
            self.parent.remove_widget(self)
            if self.clock_event:
                self.clock_event.cancel()

    def _add_to_parent(self):
        if not self.parent:
            self.orig_parent.add_widget(self)
            self.orig_parent = None
            self.hide_submenus()
            self.clock_event = Clock.schedule_interval(partial(self._check_mouse_hover), 0.05)

    # def _set_positions(self):
    #     x = self.pos[0]
    #     y = self.pos[1] - self.spacer.height
    #     # print(self.spacer.pos)
    #     for widget in self.menu_item_widgets:
    #         widget.pos = x,y
    #         # print(self.spacer.pos)
    #         # print(widget.pos)
    #         y += widget.height
    #
    #     self.spacer.pos = x,y

    @property
    def menu_item_widgets(self):
        return [w for w in self.children if issubclass(w.__class__, ContextMenuItem)]


class ContextMenuItem(object):
    hovered = kp.BooleanProperty(False)
    submenu_arrow = kp.ObjectProperty(None)
    submenu = kp.ObjectProperty(None)

    def __init__(self):
        pass
        # super(ContextMenuItem, self).__init__(**kwargs)

    def get_submenu(self):
        return self.submenu if self.submenu != "" else None
        # for widget in self.children:
        #     if issubclass(widget.__class__, ContextMenu):
        #         return widget
        # return None

    def show_submenu(self, x=None, y=None):
        if self.get_submenu():
            # print(x.pos, x.size)
            self.get_submenu().show(x, y)

    def hide_submenu(self):
        if self.get_submenu():
            self.get_submenu().visible = False

    def _update_arrows(self):
        if self.parent is not None and len(self.children) > 0:
            submenus = [w for w in self.children if issubclass(w.__class__, ContextMenu)]
            if len(submenus) > 1:
                raise Exception('Menu item (ContextMenuItem) can have maximum one submenu (ContextMenu)')
            elif len(submenus) == 1:
                self.submenu = submenus[0]
            # else:
            #     self.submenu = ""

            # print(self.get_submenu())
            if self.get_submenu() is None:
                self.submenu_arrow.opacity = 0
            else:
                self.submenu_arrow.opacity = 1

    @property
    def content_width(self):
        raise Exception('You have to overload this method.')

    # def _update_arrow_pos(self):
    #     arrow = self.submenu_arrow
    #     arrow.pos =
    #     print(arrow.pos)

class ContextMenuTextItem(ButtonBehavior, FloatLayout, ContextMenuItem):
    submenu_postfix = kp.StringProperty(' ...')
    text = kp.StringProperty('')

    def __init__(self, text=None, *args, **kwargs):
        super(ContextMenuTextItem, self).__init__(*args, **kwargs)
        if text:
            self.label.text = text

    def on_release(self):
        self.parent.visible = False

    @property
    def content_width(self):
        # keep little space for eventual arrow for submenus
        return self.label.texture_size[0] + 10

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
