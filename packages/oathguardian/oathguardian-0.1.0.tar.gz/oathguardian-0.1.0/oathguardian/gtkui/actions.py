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

import logging
import tempfile

from gi.repository import Gdk
from gi.repository import Gtk

import oathguardian
from ..tools import qrcode
from ..tools import screenshot
from .datamodel import OGModel, CredentialColumns
from .utils import load_image

log = logging.getLogger(__name__)


def debug_action(obj, action, param):
    log.info('Called %s with action=%s, param=%s',
             type(obj), action, param)


class ShowAboutAction(object):
    """
    Shows the 'about' dialog.
    """
    def __init__(self, window):
        self.parent = window

    def __call__(self, action, param):
        debug_action(self, action, param)

        about = Gtk.AboutDialog(transient_for=self.parent, modal=True)
        about.set_license_type(Gtk.License.CUSTOM)
        about.set_license(oathguardian.LICENSE_TEXT)
        about.set_copyright(oathguardian.COPYRIGHT)
        about.set_comments(oathguardian.DESCRIPTION)
        about.set_authors(oathguardian.AUTHORS)
        about.set_website(oathguardian.URL)
        about.set_version(oathguardian.VERSION)
        about.set_logo_icon_name(oathguardian.NAME)
        about.present()


class ShowAddAction(object):
    """
    Shows the 'add' dialog.
    """
    @classmethod
    def name(cls):
        return 'add_entry'

    def __init__(self, appwindow):
        self.appwindow = appwindow
        self.controller = appwindow.add_controller

    def __call__(self, action, param):
        debug_action(self, action, param)

        response = self.controller.run()

        if response == 1:
            params, provider = self.controller.validate()

            self.appwindow.app.model.add_to_provider(provider, **params)
        else:
            log.debug('%s cancelled.', self.name())

        self.controller.hide()


class ScanQRAction(object):

    @classmethod
    def name(cls):
        return 'scan_qr'

    def __init__(self, application):
        self.app = application
        self.tempfile = None

    def __call__(self, action, param=None):
        debug_action(self, action, param)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
            with screenshot.ScreenGrabber(temp.name, self.on_success, self.on_error) as sg:
                sg.grab()

    def on_success(self, result):
        success, filename = result
        data = qrcode.decode(filename)
        log.debug('%s: decoded %s from qr code', ScanQRAction.name(), data)
        self.app.add_controller.fill(**data)

    def on_error(self, result):
        log.error(result)


class GenerateAction(object):

    @classmethod
    def name(cls):
        return 'generate'

    def __init__(self, model):
        self.model = model

    def __call__(self, view, path, column):
        self.model.generate_code(path)


class CopyTokenAction(object):
    """
    Puts the current token into the clipboard.
    """
    def __init__(self, model: OGModel, view: Gtk.TreeView):
        self.model = model
        self.view = view

    @staticmethod
    def name():
        return 'copy_password'

    def __call__(self, action, param):
        debug_action(self, action, param)

        model, tree_iter = self.view.get_selection().get_selected()
        if not tree_iter:
            log.warning('%s: no current entry: action should have been deactivated!', self.name())
            return

        current = self.model.code_from_row(model[tree_iter])
        if not current:
            log.debug('%s: no current code for row, do nothing.', self.name())

        pwd = str(current.code)
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(pwd, -1)


class RemoveCredentialAction(object):
    """
    Removes the selected token.
    """
    def __init__(self, model: OGModel, view: Gtk.TreeView, window: Gtk.Window):
        self.window = window
        self.model = model
        self.view = view

    @staticmethod
    def name():
        return 'remove_credential'

    def __call__(self, action, param):
        debug_action(self, action, param)

        model, tree_iter = self.view.get_selection().get_selected()
        if not tree_iter:
            log.warning('%s: no current entry: action should have been deactivated!', self.name())
            return

        row = model[tree_iter]
        cred = row[CredentialColumns.CREDENTIAL]

        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.CANCEL,
                                   "Remove {}?".format(cred))
        dialog.format_secondary_text("This will permanently remove {credential} from {provider}.".format(
            credential=cred, provider=cred.provider.name
        ))
        dialog.add_button("Remove", Gtk.ResponseType.YES)
        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.YES:
            return

        try:
            self.model.remove(tree_iter)
        except Exception as e:
            log.error('Unable to remove %s', tree_iter, exc_info=e)


class RefreshProvidersAction(object):

    @classmethod
    def name(cls):
        return 'refresh-provider'

    def __init__(self, model):
        self.model = model

    def __call__(self, *args):
        self.model.refresh_providers()
