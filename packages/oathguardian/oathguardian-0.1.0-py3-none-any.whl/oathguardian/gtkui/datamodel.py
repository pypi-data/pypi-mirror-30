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
import time
import typing

from gi.repository import GLib
from gi.repository import Gtk

from . import utils
from .. import oath
from ..oath.providers.tools import ProviderCallback, ProviderList

log = logging.getLogger(__name__)


class CredentialColumns(utils.Columns):
    """
    Definition of the columns provided by OGModel#store store.
    """
    PROVIDER = ('Provider', object)
    CREDENTIAL = ('Credential', object)
    CODE_OBJECT = ('Code', object)
    NAME = ('Name', str)
    EXPIRATION = ('Expiration', int)
    CODE = ('Code', str)
    REMAINING_TIME = ('Remaining', int)


class ProviderColumns(utils.Columns):
    """

    """
    PROVIDER_ID = ('ID', str)
    PROVIDER = ('Provider', object)


class OGModel(ProviderCallback):
    """
    Stores the current state of oath guardian.
    """
    @classmethod
    def token_to_row(cls, token: oath.Credential, provider: oath.Provider, code=None):
        issuer = token.issuer or 'No issuer'
        assert token.name is not None

        expiration = code and code.expiry or 0
        return (provider, token, None,
                "<big>{}</big>\n{}".format(GLib.markup_escape_text(issuer),
                                           GLib.markup_escape_text(token.name)),
                expiration,
                cls._format_code(code=code),
                0)

    @classmethod
    def token_from_row(cls, row) -> oath.Credential:
        return row[CredentialColumns.CREDENTIAL]

    @classmethod
    def code_from_row(cls, row) -> oath.Code:
        return row[CredentialColumns.CODE_OBJECT]

    @classmethod
    def _compute_expiration(cls, token: oath.Credential, row, timestamp=None):
        code = cls.code_from_row(row)
        if not code:
            return 0

        expiration = row[CredentialColumns.EXPIRATION]
        if not expiration:
            return 0

        if expiration < 0:
            return 100

        if not timestamp:
            timestamp = int(time.time())

        if expiration > timestamp:
            remaining_time = expiration - timestamp
            log.debug('For token %s expiring at %d: remaining %ds',
                      token.name, expiration, remaining_time)
            return min(100, 100 * remaining_time / code.period)
        else:
            return 0

    @classmethod
    def _format_code(cls, code: oath.Code=None):
        if code:
            formatter = oath.new_human_formatter(code.digits)
            code = '<b>{}</b>'.format(GLib.markup_escape_text(formatter(code.code)))
        else:
            code = '______'

        return '<big><tt>{}</tt></big>'.format(code)

    def __init__(self, settings):
        self._credentials = Gtk.ListStore(*CredentialColumns.column_types())
        self._providers_store = Gtk.ListStore(*ProviderColumns.column_types())

        self._providers_list = ProviderList(settings)
        self._providers_list.add_listener(self)
        self._providers_list.refresh()

        self.started = True
        # Not sure it is worth it to do this every demi-second...
        # self._timer_source = GLib.timeout_add(interval=500, function=self.refresh_providers)
        self._check_expiration_source = GLib.timeout_add_seconds(interval=1, function=self._check_expiration)

    @property
    def providers(self) -> Gtk.ListStore:
        return self._providers_store

    @property
    def credentials(self) -> Gtk.ListStore:
        return self._credentials

    @property
    def default_provider_id(self) -> typing.Optional[str]:
        # FIXME default provider should be taken from user configuration
        if len(self._providers_store):
            return self._providers_store[0][0]
        return None

    def _unlock(self, provider: oath.Provider):
        if not provider.is_locked():
            return True

        return provider.unlock()

    def add_from_provider(self, provider: oath.Provider):
        self._providers_store.append([provider.id, provider])

        if not self._unlock(provider):
            # FIXME Could not unlock the provider: abort.
            return

        for token in provider.list():
            row = self.token_to_row(token, provider)
            log.debug("Adding %s -> %s from %s", token, row, provider)
            self._credentials.append(row=row)

    def add_to_provider(self, provider: oath.Provider, **kwargs):
        assert provider

        cred = provider.add(**kwargs)
        self._credentials.append(row=self.token_to_row(cred, provider))

    def remove_from_provider(self, provider: oath.Provider):
        for row in self._credentials:
            if row[CredentialColumns.PROVIDER] == provider:
                self._credentials.remove(row.iter)
        for row in self._providers_store:
            if row[ProviderColumns.PROVIDER] == provider:
                self._providers_store.remove(row.iter)

    def _check_expiration(self):
        """
        This method is periodically ran from glib thread in order to update the remaining time on each token.
        :return bool: True, to keep running.
        """
        timestamp = int(time.time())

        log.debug('Check expiration at time %d', timestamp)

        for row in self._credentials:
            token = self.token_from_row(row)
            remaining_percent = self._compute_expiration(token, row, timestamp=timestamp)
            row[CredentialColumns.REMAINING_TIME] = remaining_percent
            if not remaining_percent:
                row[CredentialColumns.CODE_OBJECT] = None
                row[CredentialColumns.CODE] = OGModel._format_code(code=None)

        return True

    def generate_code(self, path):
        row = self._credentials[path]
        if row:
            token = self.token_from_row(row)
            code = token.compute()
            log.debug('Generated %s for token %s', code, token)
            self._credentials[path][CredentialColumns.CODE_OBJECT] = code
            self._credentials[path][CredentialColumns.CODE] = self._format_code(code=code)
            self._credentials[path][CredentialColumns.EXPIRATION] = code.expiry

    def remove(self, tree_iter):
        row = self._credentials[tree_iter]
        if row:
            cred = self.token_from_row(row)
            log.info('Removing token %s', cred)

            cred.provider.remove(cred)

            self._credentials.remove(tree_iter)

    def refresh_providers(self):
        self._providers_list.refresh()
        return True

    def on_added_provider(self, provider: oath.Provider):
        log.debug('New provider added: %s (%s)', provider.name, provider.id)
        self.add_from_provider(provider)

    def on_removed_provider(self, provider: oath.Provider):
        log.debug('Provider removed: %s (%s)', provider.name, provider.id)
        self.remove_from_provider(provider)
