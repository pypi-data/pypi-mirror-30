# coding: utf-8

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

import enum
import pkgutil
import types

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GdkPixbuf
from gi.repository import Gtk


def load_uifile(filename: str, package: str=__name__) -> Gtk.Builder:
    """
    Load a glade file and return the corresponding widget tree.

    :param filename: path to file, relative to package
    :param package: package path
    :return: GTK widget tree
    :except FileNotFoundError: if the file is not found.
    """
    data = pkgutil.get_data(package, filename)
    if not data:
        raise FileNotFoundError("File {} not found in package {}".format(filename, package))
    widget_tree = Gtk.Builder()
    widget_tree.add_from_string(data.decode('utf-8'))
    return widget_tree


def load_image(filename: str, package: str=__name__) -> GdkPixbuf.Pixbuf:
    """
    Load an image file from package data, and return the pixbuf data.

    :param filename: path to image, relative to package
    :param package: package path
    :return: the image as Pixbuf object
    :except FileNotFoundError: if the image file is not found.
    """
    data = pkgutil.get_data(package, filename)
    if not data:
        raise FileNotFoundError("File {} not found in package {}".format(filename, package))

    loader = GdkPixbuf.PixbufLoader()
    loader.write(data)
    return loader.get_pixbuf()


class Columns(enum.IntEnum):
    """

    """
    def __new__(cls, name: str, data_type: type):
        value = len(cls.__members__)

        obj = int.__new__(cls, value)
        obj._value_ = value
        obj._column_name = name
        obj._data_type = data_type

        return obj

    @property
    def display_name(self):
        return self._column_name

    @property
    def data_type(self):
        return self._data_type

    @classmethod
    def column_types(cls):
        return (column.data_type for column in cls)
