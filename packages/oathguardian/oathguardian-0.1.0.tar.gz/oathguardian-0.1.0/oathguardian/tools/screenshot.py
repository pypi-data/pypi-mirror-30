# coding=utf-8

# region License

# Copyright (c) 2017,2018 Alexandre Vaissière <avaiss@fmiw.org>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# endregion

from gi.repository import GLib
from gi.repository import Gio


class ScreenGrabber(object):
    def __init__(self, filename, result_handler, error_handler):
        self.filename = filename
        self.result_handler = result_handler
        self.error_handler = error_handler

    def __enter__(self):
        self._bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self._proxy = Gio.DBusProxy.new_sync(self._bus, Gio.DBusProxyFlags.NONE, None,
                                             'org.gnome.Shell.Screenshot',
                                             '/org/gnome/Shell/Screenshot',
                                             'org.gnome.Shell.Screenshot',
                                             None)
        self._main_loop = GLib.MainLoop()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _on_error(self, obj, result, user_data):
        self.error_handler(result)

    def _on_success(self, obj, result, user_data):
        self.result_handler(result)

    def _screenshot(self, proxy, result, user_data):
        x, y, w, h = result
        proxy.ScreenshotArea('(iiiibs)',
                             x, y, w, h, False, user_data,
                             user_data=user_data,
                             result_handler=self._on_success, error_handler=self._on_error)

    def grab(self):
        self._proxy.SelectArea(timeout=5000,
                               result_handler=self._screenshot,
                               error_handler=self._on_error,
                               user_data=self.filename)
