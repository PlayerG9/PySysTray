# coding=utf-8
r"""
pystray
Copyright (C) 2021 PlayerG9

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ._util.gtk import GtkIcon, mainloop


class Icon(GtkIcon):
    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        self._status_icon = Gtk.StatusIcon.new()
        self._status_icon.connect(
            'activate', self._left_click_event)
        self._status_icon.connect(
            'popup-menu', self._right_click_event)

        if self.icon:
            self._update_icon()

    @mainloop
    def _show(self):
        self._status_icon.set_visible(True)

    @mainloop
    def _hide(self):
        self._status_icon.set_visible(False)

    @mainloop
    def _update_icon(self):
        self._remove_fs_icon()
        self._update_fs_icon()
        self._status_icon.set_from_file(self._icon_path)

    @mainloop
    def _update_title(self):
        self._status_icon.set_title(self.title)

    def _left_click_event(self, status_icon):
        """The handler for *activate* for the status icon.

        This signal handler will activate the icon.
        """
        if self.left_click:
            self.left_click()

    def _right_click_event(self, status_icon, button, activate_time):
        """The handler for *popup-menu* for the status icon.

        This signal handler will display the menu if one is set.
        """
        if self.right_click:
            self.right_click()
