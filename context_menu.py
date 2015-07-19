from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
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
    root_parent = kp.ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ContextMenu, self).__init__(*args, **kwargs)
        self.clock_event = None
        self.orig_parent = None
        self._on_visible(False)

    def add_item(self, widget):
        self.add_widget(widget)

    def add_text_item(self, text, on_release=None):
        item = ContextMenuTextItem(text)
        if on_release:
            item.bind(on_release=on_release)
        self.add_item(item)

    # def hide(self):
    #     self.visible = False

    def show(self, x=None, y=None):
        self.visible = True
        self._add_to_parent()
        self.hide_submenus()

        root_parent = self.root_parent if self.root_parent is not None else self.get_context_menu_root_parent()
        if root_parent is None:
            return

        point_relative_to_root = root_parent.to_local(*self.to_window(x, y))

        if x is not None and y is not None:
            if point_relative_to_root[0] + self.width < root_parent.width:
                pox_x = x
            else:
                pox_x = x - self.width
                if issubclass(self.parent.__class__, ContextMenuItem):
                    pox_x -= self.parent.width

            if point_relative_to_root[1] - self.height < 0:
                pos_y = y
                if issubclass(self.parent.__class__, ContextMenuItem):
                    pos_y -= self.parent.height + self.spacer.height
            else:
                pos_y = y - self.height

            parent_pos = root_parent.pos
            pos = (pox_x + parent_pos[0], pos_y + parent_pos[1])

            self.pos = pos

    def get_context_menu_root_parent(self):
        """
        Return the bounding box widget for positioning submenus. By default it's root context menu's parent.
        """
        if self.root_parent is not None:
            return self.root_parent
        root_context_menu = self._get_root_context_menu()
        return root_context_menu.root_parent if root_context_menu.root_parent else root_context_menu.parent


    def _get_root_context_menu(self):
        root = self
        while issubclass(root.parent.__class__, ContextMenuItem) \
                or issubclass(root.parent.__class__, ContextMenu):
            root = root.parent
        return root

    def _check_mouse_hover(self, obj):
        # widget_pos = self.to_window(0, 0)
        # point = self.to_local(*Window.mouse_pos)
        collided_widget = self.self_or_submenu_collide_with_point(*Window.mouse_pos)

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
            self.parent.remove_widget(self)
            self.hide_submenus()
            if self.clock_event:
                self.clock_event.cancel()

    def _add_to_parent(self):
        if not self.parent:
            self.orig_parent.add_widget(self)
            self.orig_parent = None

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

            # print(widget.to_local(x, y))
            widget_pos = widget.to_window(0, 0)
            if widget.collide_point(x - widget_pos[0], y - widget_pos[1]) and not widget.disabled:
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


class ContextMenuItem(RelativeLayout):
    submenu_arrow = kp.ObjectProperty(None)
    submenu = kp.ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ContextMenuItem, self).__init__(*args, **kwargs)

    def get_submenu(self):
        return self.submenu if self.submenu != "" else None

    def show_submenu(self, x=None, y=None):
        if self.get_submenu():
            self.get_submenu().show(*self._root_parent.to_local(x, y))

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

    @property
    def siblings(self):
        return [w for w in self.parent.children if issubclass(w.__class__, ContextMenuItem) and w != self]

    @property
    def content_width(self):
        return None

    @property
    def _root_parent(self):
        return self.parent.get_context_menu_root_parent()

    # def on_touch_down(self, click_event):
    #     super(ContextMenuItem, self).on_touch_down(click_event)
    #     return self.collide_point(click_event.x, click_event.y)


class ContextMenuHoverableItem(ContextMenuItem):
    hovered = kp.BooleanProperty(False)

    def _on_hovered(self, new_hovered):
        if new_hovered:
            point = self.right, self.top + self.parent.spacer.height
            self.show_submenu(self.width, self.height + self.parent.spacer.height)
        else:
            self.hide_submenu()


class ContextMenuText(ContextMenuItem):
    submenu_postfix = kp.StringProperty(' ...')
    text = kp.StringProperty('')
    font_size = kp.NumericProperty('14pd')

    def __init__(self, *args, **kwargs):
        super(ContextMenuText, self).__init__(*args, **kwargs)
        self.bind(text=self._on_text)
        self.bind(font_size=self._on_font_size)
        # if text:
        #     self.label.text = text

    # def on_touch_down(self, click_event):
    #     print('ContextMenuTextItem')
    #     # return True

    def _on_text(self, obj, text):
        self.label.text = text

    def _on_font_size(self, obj, size):
        self.label.font_size = size

    @property
    def content_width(self):
        # keep little space for eventual arrow for submenus
        return self.label.texture_size[0] + 10


class ContextMenuDivider(ContextMenuText):
    def on_touch_down(self, click_event):
        return self.collide_point(click_event.x, click_event.y)


class ContextMenuTextItem(ButtonBehavior, ContextMenuText, ContextMenuHoverableItem):
    pass


_path = os.path.dirname(os.path.realpath(__file__))
Builder.load_file(os.path.join(_path, 'context_menu.kv'))
