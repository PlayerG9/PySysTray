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

import functools
import logging
import threading

from six.moves import queue


class Icon(object):
    """A representation of a system tray icon.

    The icon is initially hidden. Set :attr:`visible` to ``True`` to show it.

    :param str name: The name of the icon. This is used by the system to
        identify the icon.

    :param icon: The icon to use. If this is specified, it must be a
        :class:`PIL.Image.Image` instance.

    :param str title: A short title for the icon.

    :param menu: A menu to use as popup menu. This can be either an instance of
        :class:`Menu` or a tuple, which will be interpreted as arguments to the
        :class:`Menu` constructor.

        The behaviour of the menu depends on the platform. Only one action is
        guaranteed to be invokable: the first menu item whose
        :attr:`~pystray.MenuItem.default` attribute is set.

        Some platforms allow both menu interaction and a special way of
        activating the default action, some platform allow only either an
        invisible menu with a default entry as special action or a full menu
        with no special way to activate the default item, and some platforms do
        not support a menu at all.

    :param kwargs: Any non-standard platform dependent options. These should be
        prefixed with the platform name thus: ``appindicator_``, ``darwin_``,
        ``gtk_``, ``win32_`` or ``xorg_``.

        Supported values are:

        ``darwin_nsapplication``
            An ``NSApplication`` instance used to run the event loop. If this
            is not specified, the shared application will be used.
    """
    #: Whether this particular implementation has a default action that can be
    #: invoked in a special way, such as clicking on the icon.
    HAS_DEFAULT_ACTION = True

    #: Whether this particular implementation supports menus.
    HAS_MENU = True

    #: Whether this particular implementation supports displaying mutually
    #: exclusive menu items using the :attr:`MenuItem.radio` attribute.
    HAS_MENU_RADIO = True

    #: Whether this particular implementation supports displaying a
    #: notification.
    HAS_NOTIFICATION = True

    def __init__(
            self, name, icon=None, title=None, left_click=None, right_click=None, **kwargs):
        self._name = name
        self._icon = icon or None
        self._title = title or ''
        self.left_click = left_click
        self.right_click = right_click
        self._visible = False
        self._icon_valid = False
        self._log = logging.getLogger(__name__)

        self._running = False
        self.__queue = queue.Queue()

        prefix = self.__class__.__module__.rsplit('.', 1)[-1][1:] + '_'  # no idea what this does
        self._options = {
            key[len(prefix):]: value
            for key, value in kwargs.items()
            if key.startswith(prefix)}

    def __del__(self):
        if self.visible:
            self._hide()

    @property
    def name(self):
        """The name passed to the constructor.
        """
        return self._name

    @property
    def icon(self):
        """The current icon.

        Setting this to a falsy value will hide the icon. Setting this to an
        image while the icon is hidden has no effect until the icon is shown.
        """
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self._icon_valid = False
        if value:
            if self.visible:
                self._update_icon()
        else:
            if self.visible:
                self.visible = False

    @property
    def title(self):
        """The current icon title.
        """
        return self._title

    @title.setter
    def title(self, value):
        if value != self._title:
            self._title = value
            if self.visible:
                self._update_title()

    @property
    def visible(self):
        """Whether the icon is currently visible.

        :raises ValueError: if set to ``True`` and no icon image has been set
        """
        return self._visible

    @visible.setter
    def visible(self, value):
        if self._visible == value:
            return

        if value:
            if not self._icon:
                raise ValueError('cannot show icon without icon data')

            if not self._icon_valid:
                self._update_icon()
            self._show()
            self._visible = True

        else:
            self._hide()
            self._visible = False

    def run(self, setup=None):
        """Enters the loop handling events for the icon.

        This method is blocking until :meth:`stop` is called. It *must* be
        called from the main thread.

        :param callable setup: An optional callback to execute in a separate
            thread once the loop has started. It is passed the icon as its sole
            argument.

            If not specified, a simple setup function setting :attr:`visible`
            to ``True`` is used. If you specify a custom setup function, you
            must explicitly set this attribute.
        """
        self._start_setup(setup)
        self._run()

    def run_detached(self, setup=None):
        """Prepares for running the loop handling events detached.

        This allows integrating *pystray* with other libraries requiring a
        mainloop. Call this method before entering the mainloop of the other
        library.

        Depending on the backend used, calling this method may require special
        preparations:

        macOS
            You must pass the argument ``darwin_nsapplication`` to the
            constructor. This is to ensure that you actually have a reference
            to the application instance used to drive the icon.

        :param callable setup: An optional callback to execute in a separate
            thread once the loop has started. It is passed the icon as its sole
            argument.

            If not specified, a simple setup function setting :attr:`visible`
            to ``True`` is used. If you specify a custom setup function, you
            must explicitly set this attribute.

        :raises NotImplementedError: if this is not implemented for the
            preparations taken
        """
        self._start_setup(setup)
        self._run_detached()

    def stop(self):
        """Stops the loop handling events for the icon.
        """
        self._stop()
        if self._setup_thread.ident != threading.current_thread().ident:
            self._setup_thread.join()
        self._running = False

    def notify(self, message, title=None):
        """Displays a notification.

        The notification will generally be visible until
        :meth:`remove_notification` is called.

        The class field :attr:`HAS_NOTIFICATION` indicates whether this feature
        is supported on the current platform.

        :param str message: The message of the notification.

        :param str title: The title of the notification. This will be replaced
            with :attr:`title` if ``None``.
        """

        self._notify(message, title)

    def remove_notification(self):
        """Remove a notification.
        """
        self._remove_notification()

    def _mark_ready(self):
        """Marks the icon as ready.

        The setup callback passed to :meth:`run` will not be called until this
        method has been invoked.

        Before the setup method is scheduled to be called, :meth:`update_menu`
        is called.
        """
        self._running = True
        self.__queue.put(True)

    def _handler(self, callback):
        """Generates a callback handler.

        This method is used in platform implementations to create callback
        handlers. It will return a function taking any parameters, which will
        call ``callback`` with ``self`` and then call :meth:`update_menu`.

        :param callable callback: The callback to wrap.

        :return: a wrapped callback
        """
        @functools.wraps(callback)
        def inner(*_, **__):
            callback(self)

        return inner

    def _show(self):
        """The implementation of the :meth:`show` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _hide(self):
        """The implementation of the :meth:`hide` method.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _update_icon(self):
        """Updates the image for an already shown icon.

        This method should self :attr:`_icon_valid` to ``True`` if the icon is
        successfully updated.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _update_title(self):
        """Updates the title for an already shown icon.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _run(self):
        """Runs the event loop.

        This method must call :meth:`_mark_ready` once the loop is ready.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _run_detached(self):
        """Runs detached.

        This method must call :meth:`_mark_ready` once ready.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _start_setup(self, setup):
        """Starts the setup thread.

        :param callable setup: The thread handler.
        """
        def setup_handler():
            self.__queue.get()
            if setup:
                setup(self)
            else:
                self.visible = True

        self._setup_thread = threading.Thread(target=setup_handler)
        self._setup_thread.start()

    def _stop(self):
        """Stops the event loop.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _notify(self, message, title=None):
        """Show a notification.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()

    def _remove_notification(self):
        """Remove a notification.

        This is a platform dependent implementation.
        """
        raise NotImplementedError()
