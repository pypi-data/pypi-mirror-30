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


import typing

from gi.repository import Gtk

from oathguardian.gtkui.datamodel import ProviderColumns
from . import actions
from oathguardian.gtkui import datamodel
from oathguardian.oath import OATHType, HashAlgo


class AddDialog(object):
    def __init__(self, main_window, widgets):
        self.og_model = main_window.app.model  # type: datamodel.OGModel

        self.add_dialog = widgets.get_object('add_dialog')
        self.add_dialog.set_transient_for(main_window.window)

        self.add_oath_type = widgets.get_object('add_oath_type')
        self.add_label = widgets.get_object('add_label')
        self.add_issuer = widgets.get_object('add_issuer')
        self.add_secret = widgets.get_object('add_secret')
        self.add_algorithm = widgets.get_object('add_algorithm')
        self.add_digits = widgets.get_object('add_digits')
        self.add_period = widgets.get_object('add_period')
        self.add_counter = widgets.get_object('add_counter')
        self.add_touch = widgets.get_object('add_touch')
        self.add_provider = widgets.get_object('add_storage')

        scan_button = widgets.get_object('add_scan_button')
        scan_button.connect("clicked", actions.ScanQRAction(main_window))

        oath_type_store = Gtk.ListStore(str, str, object)
        for item in OATHType:
            oath_type_store.append([item.value, item.name, item])
        self.add_oath_type.set_model(oath_type_store)
        self.add_oath_type.set_id_column(0)
        self.add_oath_type.set_entry_text_column(1)

        algorithm_store = Gtk.ListStore(str, str, object)
        for item in HashAlgo:
            algorithm_store.append([item.value, item.name, item])
        self.add_algorithm.set_model(algorithm_store)
        self.add_algorithm.set_id_column(0)
        self.add_algorithm.set_entry_text_column(1)

        self.add_provider.set_model(self.og_model.providers)
        self.add_provider.set_id_column(0)
        self.add_provider.set_entry_text_column(1)
        self.add_provider.set_active_id(self.og_model.default_provider_id)

    def run(self):
        return self.add_dialog.run()

    def hide(self):
        return self.add_dialog.hide()

    def fill(self, **kwargs):
        oath_type = kwargs.get('oath_type')

        self.add_oath_type.set_active_id(oath_type)
        self.add_label.set_text(kwargs.get('label', ''))
        self.add_issuer.set_text(kwargs.get('issuer', ''))
        self.add_secret.set_text(kwargs.get('secret', ''))
        self.add_algorithm.set_active_id(kwargs.get('algorithm', '').lower())
        self.add_digits.set_value(kwargs.get('digits', 0))

        # Those should depend on oath_type
        self.add_period.set_value(kwargs.get('period', 0))
        self.add_counter.set_value(kwargs.get('counter', 0))

        self.add_provider.set_active_id(self.og_model.default_provider_id)

        # For now, always set require_touch to true.
        self.add_touch.set_state(True)

    def validate(self):
        oath_type_iter = self.add_oath_type.get_active_iter()
        if not oath_type_iter:
            raise Exception('No valid auth type')

        oath_type = self.add_oath_type.get_model()[oath_type_iter][2]
        label = self.add_label.get_text()
        secret = self.add_secret.get_text()
        digits = self.add_digits.get_value_as_int()
        issuer = self.add_issuer.get_text()
        touch = self.add_touch.get_state()

        result = {
            'oath_type': oath_type,
            'label': label,
            'secret': secret,
            'digits': digits,
            'issuer': issuer,
            'require_touch': touch,
        }

        algo_iter = self.add_algorithm.get_active_iter()
        if algo_iter:
            result['algorithm'] = self.add_algorithm.get_model()[algo_iter][2]

        if oath_type == OATHType.TOTP:
            result['period'] = self.add_period.get_value_as_int()

        if oath_type == OATHType.HOTP:
            result['counter'] = self.add_counter.get_value_as_int()

        provider_iter = self.add_provider.get_active_iter()
        if not provider_iter:
            raise Exception('No provider selected!')
        provider = self.og_model.providers[provider_iter][ProviderColumns.PROVIDER]

        return result, provider


class PasswordDialog(object):
    DEFAULT_PROMPT = 'Please enter password'

    def __init__(self, widgets):
        self._dialog = widgets.get_object('password_dialog')
        self._dialog.set_default_response(Gtk.ResponseType.OK)

        self._label = widgets.get_object('password_label')
        self._password = widgets.get_object('password_entry')

        self._password.connect('icon-press', PasswordDialog._show_password)
        self._password.connect('activate', self._activate)

    def ask_password(self, prompt: str=None) -> typing.Union[str, None]:
        """
        :return: password entered by user, or None if user cancelled the request.
        """
        self._label.set_text(prompt or PasswordDialog.DEFAULT_PROMPT)

        try:
            while True:
                resp = self._dialog.run()
                if resp != Gtk.ResponseType.OK:
                    return None

                text = self._password.get_text()
                if text:
                    return text
        finally:
            self._reset()
            self._dialog.hide()

    def _reset(self):
        self._password.set_text('')

    def _activate(self, *args):
        self._dialog.response(Gtk.ResponseType.OK)

    @classmethod
    def _show_password(cls, entry, pos, *args, **kwargs):
        if pos == Gtk.EntryIconPosition.SECONDARY:
            entry.set_visibility(not entry.get_visibility())
