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


import logging

from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk

import oathguardian
from . import controllers
from . import actions
from . import datamodel
from .utils import load_uifile
from oathguardian.oath import config

log = logging.getLogger(__name__)


class MainWindow(object):
    """Wrapper around the main application window."""
    def __init__(self, application, title=None):
        super(MainWindow, self).__init__()
        self.app = application

        widget_tree = load_uifile('oathguardian.xml')
        self.window = widget_tree.get_object('mainwindow')
        self.__configure_window(application, title)

        self.tokens_view = widget_tree.get_object('tokens_view')
        self.__init_treeview(self.tokens_view, self.app.model)

        self.add_controller = controllers.AddDialog(self, widget_tree)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", actions.ShowAboutAction(self.window))
        self.app.add_action(action)

        action = Gio.SimpleAction.new('refresh', None)
        action.connect('activate', actions.RefreshProvidersAction(self.app.model))
        self.app.add_action(action)
        self.app.add_accelerator('<Control>R', 'app.refresh', None)

        action = Gio.SimpleAction.new("add", None)
        action.connect("activate", actions.ShowAddAction(self))
        self.app.add_action(action)
        self.app.add_accelerator('<Control>N', 'app.add', None)

        action = Gio.SimpleAction.new("copy", None)
        action.connect("activate", actions.CopyTokenAction(self.app.model, self.tokens_view))
        self.app.add_action(action)
        self.app.add_accelerator('<Control>C', 'app.copy', None)

        action = Gio.SimpleAction.new("remove", None)
        action.connect("activate", actions.RemoveCredentialAction(self.app.model, self.tokens_view, self.window))
        self.app.add_action(action)
        self.app.add_accelerator('Delete', 'app.remove', None)

        # This will be in the windows group and have the "win" prefix
        max_action = Gio.SimpleAction.new_stateful("maximize", None, GLib.Variant.new_boolean(False))
        max_action.connect("change-state", self.on_maximize_toggle)
        self.window.add_action(max_action)

        # Keep it in sync with the actual state
        self.window.connect("notify::is-maximized",
                            lambda obj, pspec: max_action.set_state(GLib.Variant.new_boolean(obj.props.is_maximized)))

    def __configure_window(self, application, title):
        self.window.set_application(application)
        if title:
            self.window.set_title(title)

    def __init_treeview(self, view: Gtk.TreeView, model: datamodel.OGModel):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(datamodel.CredentialColumns.NAME.display_name,
                                    cell_renderer=renderer, markup=datamodel.CredentialColumns.NAME)
        view.append_column(column)

        renderer = Gtk.CellRendererProgress()
        renderer.set_orientation(Gtk.Orientation.VERTICAL)
        renderer.set_property('inverted', True)
        renderer.set_property('text', '')
        column = Gtk.TreeViewColumn(datamodel.CredentialColumns.REMAINING_TIME.display_name,
                                    cell_renderer=renderer, value=datamodel.CredentialColumns.REMAINING_TIME)
        view.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(datamodel.CredentialColumns.CODE.display_name,
                                    cell_renderer=renderer, markup=datamodel.CredentialColumns.CODE)
        view.append_column(column)

        view.connect('row-activated', actions.GenerateAction(model))
        view.set_model(model.credentials)
        view.set_search_column(datamodel.CredentialColumns.NAME)
        view.set_enable_search(True)
        view.set_search_equal_func(self._search)

    @staticmethod
    def _search(model, column, search, row_iter, user_data=None):
        value = model[row_iter][column]
        return value and search and search not in value

    def present(self):
        self.window.present()

    def on_maximize_toggle(self, action, value):
        action.set_state(value)
        if value.get_boolean():
            self.window.maximize()
        else:
            self.window.unmaximize()


class OathGuardian(Gtk.Application):
    """Application."""
    def __init__(self, *args, **kwargs):
        super(Gtk.Application, self).__init__(*args, application_id="org.fmiw.oathguardian",
                                              #flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                                              **kwargs)
        GLib.set_application_name(oathguardian.NAME)
        GLib.set_prgname(oathguardian.NAME)

        self.window = None
        self.provider = None
        self.model = None
        self.config = config.Config()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.config.load_config()

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self._on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self._on_quit)
        self.add_action(action)

        builder = load_uifile('oathguardian_menu.xml')
        self.set_app_menu(builder.get_object("app-menu"))

        self.model = datamodel.OGModel(self.config)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = MainWindow(application=self, title=oathguardian.TITLE)

        self.window.present()

    def _on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()

    def _on_quit(self, action, param):
        self.quit()
