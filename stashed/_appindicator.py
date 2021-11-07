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

try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as AppIndicator
except ValueError:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator

from ._util.gtk import GtkIcon, mainloop
from . import _base


class Icon(GtkIcon):
    # We expand the menu on primary button click, and we do not even support
    # empty menus
    HAS_DEFAULT_ACTION = False

    def __init__(self, *args, **kwargs):
        super(Icon, self).__init__(*args, **kwargs)

        self._appindicator = None

        if self.icon:
            self._update_icon()

    @mainloop
    def _show(self):
        self._appindicator = AppIndicator.Indicator.new(
            self.name,
            '',
            AppIndicator.IndicatorCategory.APPLICATION_STATUS)

        self._appindicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self._appindicator.set_icon(self._icon_path)
        self._appindicator.set_menu(
            self._menu_handle or self._create_default_menu())

    @mainloop
    def _hide(self):
        self._appindicator = None

    @mainloop
    def _update_icon(self):
        self._remove_fs_icon()
        self._update_fs_icon()
        if self._appindicator:
            self._appindicator.set_icon(self._icon_path)

    @mainloop
    def _update_title(self):
        self._appindicator.set_title(self.title)

    def _finalize(self):
        super(Icon, self)._finalize()
        del self._appindicator
