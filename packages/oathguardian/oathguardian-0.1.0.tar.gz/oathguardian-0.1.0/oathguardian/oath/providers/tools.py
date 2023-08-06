# coding: utf-8

# region License

# Copyright (c) 2018 Alexandre Vaissière <avaiss@fmiw.org>
#
# Permission to use, copy, modify, and/or distribute this software for any
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

"""

"""

from . import Provider
from . import local, yubikey


class ProviderCallback(object):
    """

    """
    def on_added_provider(self, provider: Provider):
        pass

    def on_removed_provider(self, provider: Provider):
        pass


class ProviderList(object):
    """Contains the list of current providers.
    Each call to refresh method query the system for current list of plugged yubikeys.
    """
    def __init__(self, settings):
        self._contents = {}
        self._callbacks = []

        # By default we load the secret storage default one.
        dflt = local.default()
        self._contents[dflt.id] = dflt

        self._yubikey_finder = yubikey.get_finder(settings)

    def __iter__(self):
        return iter(self._contents.values())

    def add_listener(self, listener: ProviderCallback) -> bool:
        if listener in self._callbacks:
            return False
        self._callbacks.append(listener)

        # send current contents
        for item in self._contents.values():
            listener.on_added_provider(item)

        return True

    def remove_listener(self, listener: ProviderCallback):
        self._callbacks.remove(listener)

    def _emit_added(self, provider):
        for callback in self._callbacks:
            callback.on_added_provider(provider)

    def _emit_removed(self, provider):
        for callback in self._callbacks:
            callback.on_removed_provider(provider)

    def refresh(self):
        if not self._yubikey_finder:
            return

        added, removed = self._yubikey_finder.update_readers()

        # notify of removed providers
        for id_removed in removed:
            prov = self._contents.pop(id_removed)
            self._emit_removed(prov)

        # creates new providers
        for desc in added:
            prov = desc.open()
            self._contents[desc.id] = prov
            self._emit_added(prov)
