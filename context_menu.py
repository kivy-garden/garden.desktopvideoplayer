import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
# from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.clock import Clock
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
        self.hide_submenus()

        root_parent = self._get_context_menu_root_parent()
        if root_parent is None:
            return

        if x is not None and y is not None:
            if x + self.width < root_parent.width:
                pox_x = x
            else:
                pox_x = x - self.width
                if issubclass(self.parent.__class__, ContextMenuItem) :
                    pox_x -= self.parent.width

            if y - self.height < 0:
                pos_y = y
                if issubclass(self.parent.__class__, ContextMenuItem) :
                    pos_y -= self.parent.height + self.spacer.height
            else:
                pos_y = y - self.height

            parent_pos = root_parent.pos
            pos = (pox_x + parent_pos[0], pos_y + parent_pos[1])

            self.pos = pos
            # print(self.pos)
            # self._set_positions()

    def _get_context_menu_root_parent(self):
        context_root_parent = self.parent
        while issubclass(context_root_parent.__class__, ContextMenuItem) \
                or issubclass(context_root_parent.__class__, ContextMenu):
            context_root_parent = context_root_parent.parent
        return context_root_parent

    def _get_root_context_menu(self):
        root = self
        while issubclass(root.parent.__class__, ContextMenuItem) \
                or issubclass(root.parent.__class__, ContextMenu):
            root = root.parent
        return root


    def _check_mouse_hover(self, obj):
        point = self.to_local(*Window.mouse_pos)
        collided_widget = self.self_or_submenu_collide_with_point(*point)

    def get_height(self):
        height = 0
        for widget in self.children:
            height += widget.height
        return height

    def get_max_width(self):
        max_width = 0
        for widget in self.menu_item_widgets:
            width = widget.content_width if widget.content_width is not None else widget.width
            if width is not None and width > max_width:
                max_width = width

        return max_width

    def hide_submenus(self):
        for widget in self.menu_item_widgets:
            widget.hovered = False
            widget.hide_submenu()

    def _on_visible(self, new_visibility):
        if new_visibility:
            self.size = self.get_max_width(), self.get_height()
            self._add_to_parent()
        elif self.parent and not new_visibility:
            self.orig_parent = self.parent
            # self.parent.submenu = self
            self.parent.remove_widget(self)
            self.hide_submenus()
            if self.clock_event:
                self.clock_event.cancel()

    def _add_to_parent(self):
        if not self.parent:
            self.orig_parent.add_widget(self)
            self.orig_parent = None

            # self.hide_submenus()
            if self._get_root_context_menu() == self:
                self.clock_event = Clock.schedule_interval(partial(self._check_mouse_hover), 0.05)

    def self_or_submenu_collide_with_point(self, x, y):
        queue = self.menu_item_widgets
        collide_widget = None
        while len(queue) > 0:
            widget = queue.pop(0)
            submenu = widget.get_submenu()
            if submenu is not None:
                queue += submenu.menu_item_widgets

            if widget.collide_point(x, y):
                widget.hovered = True
                collide_widget = widget
                for sib in widget.siblings:
                    sib.hovered = False
                # break
            elif submenu and submenu.visible:
                widget.hovered = True
            else:
                widget.hovered = False

        return collide_widget

    @property
    def menu_item_widgets(self):
        return [w for w in self.children if issubclass(w.__class__, ContextMenuItem)]


class ContextMenuItem(object):
    hovered = kp.BooleanProperty(False)
    submenu_arrow = kp.ObjectProperty(None)
    submenu = kp.ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ContextMenuItem, self).__init__(*args, **kwargs)

    def get_submenu(self):
        return self.submenu if self.submenu != "" else None

    def show_submenu(self, x=None, y=None):
        if self.get_submenu():
            self.get_submenu().show(x, y)

    def hide_submenu(self):
        submenu = self.get_submenu()
        if submenu:
            submenu.visible = False
            submenu.hide_submenus()

    def _update_arrows(self):
        if self.parent is not None and len(self.children) > 0:
            submenus = [w for w in self.children if issubclass(w.__class__, ContextMenu)]
            if len(submenus) > 1:
                raise Exception('Menu item (ContextMenuItem) can have maximum one submenu (ContextMenu)')
            elif len(submenus) == 1:
                self.submenu = submenus[0]
            # else:
            #     self.submenu = ""

            if self.get_submenu() is None:
                self.submenu_arrow.opacity = 0
            else:
                self.submenu_arrow.opacity = 1

    def _on_hovered(self, new_hovered):
        if new_hovered:
            self.show_submenu(self.right, self.top + self.parent.spacer.height)
        else:
            self.hide_submenu()

    # def on_touch_down(self, click_event):
    #     print(click_event)
    #     return True

    @property
    def siblings(self):
        return [w for w in self.parent.children if issubclass(w.__class__, ContextMenuItem) and w != self]

    @property
    def content_width(self):
        return None


class ContextMenuTextItem(ButtonBehavior, FloatLayout, ContextMenuItem):
    submenu_postfix = kp.StringProperty(' ...')
    text = kp.StringProperty('')

    def __init__(self, text=None, *args, **kwargs):
        super(ContextMenuTextItem, self).__init__(*args, **kwargs)
        if text:
            self.label.text = text

    # def on_touch_down(self, click_event):
    #     print('ContextMenuTextItem')
    #     # return True

    def on_release(self):
        pass

    @property
    def content_width(self):
        # keep little space for eventual arrow for submenus
        return self.label.texture_size[0] + 10


_path = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(os.path.join(_path, 'context_menu.kv'))