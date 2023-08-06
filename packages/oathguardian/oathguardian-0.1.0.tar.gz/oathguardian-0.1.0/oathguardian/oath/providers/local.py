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

import secretstorage
import secretstorage.collection

import oathguardian
from oathguardian import oath
from oathguardian.oath import errors
from oathguardian.oath.providers import ProviderCapability

log = logging.getLogger(__name__)


class LocalProvider(oath.Provider):
    """
    The local provider stores secret in gnome keyring (or any application
    implementing the freedesktop secret interface).
    """
    def __init__(self, collection: secretstorage.Collection):
        self.collection = collection
        self._id = 'local:' + collection.get_label()

    @staticmethod
    def make_name(label: str, issuer: str=None) -> str:
        if not issuer:
            return label

        if label.startswith(issuer + ':'):
            return label

        return issuer + ':' + label

    def add(self, oath_type: oath.OATHType, label: str, secret: oath.key_types,
            issuer: str=None, algorithm: oath.HashAlgo=oath.HashAlgo.SHA1, digits: int=6,
            counter: int=None, period: int=30, **kwargs) -> oath.Credential:
        if oath_type not in (oath.OATHType.TOTP, oath.OATHType.HOTP):
            raise errors.UnsupportedOATHTypeError('{} does not support {} types'.format(self, oath_type))

        key_bytes = oath.to_b32_key(secret).encode('utf-8')

        options = {
            'oath_type': oath_type.name.lower(),
            'algorithm': algorithm.value,
            'issuer': issuer,
            'digits': str(digits),
            'created-by': oathguardian.NAME,
        }

        if oath_type == oath.OATHType.TOTP:
            options.update({'period': str(period)})
        elif oath_type == oath.OATHType.HOTP:
            options.update({'counter': str(counter)})

        name = self.make_name(label, issuer)

        log.info('Adding %s -> %s to %s collection.', name, options, self.collection.get_label())

        item = self.collection.create_item(name, options, key_bytes)
        return LocalCredential(self, item)

    def list(self):
        if self.collection.is_locked():
            raise Exception('Collection is locked!')

        def is_cred(item):
            attrs = item.get_attributes()
            return oathguardian.NAME == attrs.get('created-by') and attrs.get('oath_type') in ('totp', 'hotp')

        return [self._wrap(item) for item in self.collection.get_all_items() if is_cred(item)]

    def _wrap(self, item: secretstorage.Item) -> oath.Credential:
        return LocalCredential(self, item)

    def unlock(self):
        self.collection.unlock(self._on_unlock)
        return not self.collection.is_locked()

    def _on_unlock(self, dismissed, items):
        if not dismissed:
            log.info('Unlocked collection %s (containing %d items)', self.id, len(items))
        else:
            log.info('User dismissed the password prompt.')

    def remove(self, cred):
        if cred.provider != self:
            raise ValueError('credential {} does not come from {}'.format(cred, self.id))
        cred._item.delete()

    @property
    def capabilities(self):
        return ProviderCapability.TOTP | ProviderCapability.LOCK

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return '{collection_name} keyring'.format(collection_name=self.collection.get_label())

    def is_locked(self):
        return self.collection.is_locked()


class LocalCredential(oath.Credential):

    def __init__(self, provider, item: secretstorage.Item):
        attrs = item.get_attributes()
        label, issuer = oath.uri.normalize_name(item.get_label(), attrs.get('issuer'))
        super(LocalCredential, self).__init__(label, issuer=issuer)

        self._digits = int(attrs.get('digits'))
        self._provider = provider
        self._item = item
        self._algorithm = oath.HashAlgo[attrs.get('algorithm').upper()]
        self._type = oath.OATHType[attrs.get('oath_type').upper()]
        self._period = int(attrs.get('period', 0))
        self._counter = int(attrs.get('counter', 0))

    @property
    def provider(self):
        return self._provider

    @property
    def type(self) -> oath.OATHType:
        return self._type

    def _fetch_key(self) -> bytes:
        return self._item.get_secret()

    def _compute0(self, **kwargs) -> typing.Tuple[int, int, int, int]:
        key = self._fetch_key()

        if self.type == oath.OATHType.TOTP:
            timestamp = int(time.time())
            totp = oath.generate_totp(key, timestamp=timestamp, period=self._period, digits=self._digits,
                                      hash_algo=self._algorithm.value)
            return totp, self._digits, (timestamp//self._period + 1) * self._period, self._period

        if self.type == oath.OATHType.HOTP:
            hotp = oath.generate_hotp(key, counter=self._counter, digits=self._digits, hash_algo=self._algorithm.value)

            # Update counter in our item.
            attrs = self._item.get_attributes()
            self._counter += 1
            attrs['counter'] = str(self._counter)
            self._item.set_attributes(attrs)

            return hotp, self._digits, -1, -1


def find_providers(known=None):
    if 'oathguardian' in known:
        return

    bus = secretstorage.dbus_init()
    for collection in secretstorage.get_all_collections(bus):
        if 'oathguardian' == collection.get_label():
            yield LocalProvider(collection)
            return

    collection = secretstorage.create_collection(bus, 'oathguardian')
    yield LocalProvider(collection)


def default() -> LocalProvider:
    """
    Gets a provider that store all credentials on secret-service default collection.
    :return: the default provider.
    """
    bus = secretstorage.dbus_init()
    collection = secretstorage.get_default_collection(bus)
    return LocalProvider(collection)
