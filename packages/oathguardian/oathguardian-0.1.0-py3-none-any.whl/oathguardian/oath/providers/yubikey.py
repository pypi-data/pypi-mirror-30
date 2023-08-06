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

"""
Yubikey 4 provider implementation.
"""

import logging
import time
import typing

import smartcard.Exceptions

import ykman.oath as ykoath
from ykman import driver_ccid

from . import Provider, ProviderCapability, Credential, OATHType, HashAlgo
from .. import errors
from .. import config
from ... import oath

from oathguardian.tools import gnupg

log = logging.getLogger(__name__)


class YubikeyOath(Provider):
    """
    Oath provider using YKOATH protocol (yubikey 4).
    """

    def __init__(self, settings: config.Config, driver: driver_ccid.CCIDDriver):
        self.settings = settings
        self.driver = driver
        self.controller = ykoath.OathController(driver)

    @property
    def name(self):
        return '{} {}'.format(self.driver.key_type.value, self.driver.serial)

    @property
    def id(self) -> str:
        return 'yubikey:{}'.format(self.driver.serial)

    @property
    def capabilities(self) -> ProviderCapability:
        return ProviderCapability.TOTP | ProviderCapability.HOTP | ProviderCapability.LOCK

    @classmethod
    def _to_yubikey_credential(cls, orig: oath.Credential) -> ykoath.Credential:
        if isinstance(orig, YubiCredential):
            return orig._yubi_cred
        raise ValueError('credential {} does not come from yubikey'.format(orig))

    def remove(self, cred: Credential):
        self.controller.delete(YubikeyOath._to_yubikey_credential(cred))

    def add(self, oath_type: OATHType, label: str, secret: oath.key_types,
            issuer: str = None, algorithm: HashAlgo = HashAlgo.SHA1, digits: int = 6,
            counter: int = None, period: int = 30, **kwargs):
        if oath_type not in (oath.OATHType.TOTP, oath.OATHType.HOTP):
            raise errors.UnsupportedOATHTypeError('{} does not support {} types'.format(self, oath_type))

        key_bytes = oath.to_binary_key(secret)

        if not counter:
            counter = 0

        data = ykoath.CredentialData(key_bytes, issuer, label, oath_type=ykoath.OATH_TYPE[oath_type.name],
                                     algorithm=ykoath.ALGO[algorithm.name], digits=digits, period=period,
                                     counter=counter, touch=kwargs.get('require_touch', True))

        log.info('Adding %s to %s', data.make_key(), self)

        try:
            cred = self.controller.put(data)
            return self._wrap(cred)
        except ykoath.APDUError as e:
            if e.sw == ykoath.SW.NO_SPACE:
                raise errors.NoSpaceLeftError('No space left on device.')
            elif e.sw == ykoath.SW.COMMAND_ABORTED:
                raise errors.NoSpaceLeftError('The command failed. Do you have enough space on the device?')
            else:
                raise

    def list(self):
        return [self._wrap(cred) for cred in self.controller.list()]

    def _wrap(self, cred: ykoath.Credential) -> Credential:
        return YubiCredential(self, cred)

    def is_locked(self):
        return self.controller.locked

    def unlock(self):
        with gnupg.pinentry(self.settings.pinentry_executable()) as pinentry:
            pinentry.set_option('allow-external-password-cache')
            pinentry.set_keyinfo('oathguardian: ' + self.id)

            for attempt in range(3):
                try:
                    password = pinentry.ask_pin('Please enter passphrase for {}'.format(self.id))
                except gnupg.AssuanError as e:
                    log.error("Could not get pin from user: 0x%x %s", e.code, e)
                    return

                key = self.controller.derive_key(password)
                try:
                    self.controller.validate(key)
                    return True
                except Exception as e:
                    log.error('Unable to unlock: %s', e, exc_info=e)
                    pinentry.set_error('Invalid password. Remaining {} attempts.'.format(2 - attempt))

    def __del__(self):
        log.info('Releasing %s', self.name)
        del self.controller._driver

    def __str__(self):
        return self.id

    def __repr__(self):
        return 'YubikeyOath<{}>'.format(self.id)


class YubiCredential(oath.Credential):
    def __init__(self, provider: YubikeyOath, yubi_cred: ykoath.Credential):
        super(YubiCredential, self).__init__(yubi_cred.name, issuer=yubi_cred.issuer)
        self._yubi_cred = yubi_cred
        self._provider = provider
        self._type = oath.OATHType[yubi_cred.oath_type.name]

    @property
    def provider(self):
        return self._provider

    @property
    def type(self) -> OATHType:
        return self._type

    def _compute0(self, **kwargs) -> typing.Tuple[int, int, int, int]:
        code = self._provider.controller.calculate(self._yubi_cred)

        expiry = code.valid_to
        if self._yubi_cred.oath_type == ykoath.OATH_TYPE.HOTP:
            expiry = -1

        # FIXME does not work every time if the credential is named steam.
        return int(code.value), len(code.value), expiry, self._yubi_cred.period


class _ProviderDescriptor(object):
    def __init__(self, settings, drv: driver_ccid.CCIDDriver):
        self._settings = settings
        self._driver = drv

    @property
    def id(self):
        return 'yubikey:{}'.format(self._driver.serial)

    def open(self):
        return YubikeyOath(self._settings, self._driver)

    def __del__(self):
        del self._driver


class _YubikeyFinder(object):
    """Finds currently plugged in yubikeys and opens them. This instance stores the currently
    known keys, so that they are not opened several times; and permits consecutive calls to
    :func:`update_readers` to return a list of added and removed keys.
    """
    def __init__(self, settings):
        """

        :param config.Config settings: oathguardian configuration.
        """
        self.settings = settings
        self._cards = {}
        self._attempts = 3

    def _open_reader(self, reader):
        attempt = 0
        while True:
            sleep_time = (attempt + 1) * 0.1
            try:
                conn = reader.createConnection()
                conn.connect()
                return driver_ccid.CCIDDriver(conn, reader.name)
            except smartcard.Exceptions.CardConnectionException as e:
                log.error("Could not open CCID: %s", str(e), exc_info=e)
                if attempt < self._attempts:
                    attempt += 1
                    gnupg.kill_scdaemon(socket_path=self.settings.gpg_agent_path())
                    time.sleep(sleep_time)
                    continue
                raise

    def update_readers(self):
        log.debug('Updating readers, known being %s', self._cards.keys())

        current_readers = {reader.name: reader for reader in driver_ccid._list_readers()
                           if reader.name.lower().startswith('yubico yubikey')}

        known_names = set(self._cards.keys())
        current_names = set(current_readers.keys())

        # handle removed readers
        removed = []
        removed_names = known_names - current_names
        for name in removed_names:
            desc = self._cards.pop(name)
            removed.append(desc.id)
            del desc

        added = []
        added_names = current_names - known_names
        for name in added_names:
            try:
                driver = self._open_reader(current_readers[name])
                desc = _ProviderDescriptor(self.settings, driver)
                self._cards[name] = desc
                added.append(desc)
            except smartcard.Exceptions.CardConnectionException as e:
                log.warning('Could not open %s: %s', name, str(e), exc_info=e)
                continue

        log.debug('New cards added: %s, removed: %s', added, removed)

        return added, removed


def get_finder(settings):
    """
    :param config.Config settings:
    :return:
    """
    # Try to disable this code in case pcscd is not enabled or launched or does not work.

    from smartcard.pcsc.PCSCContext import PCSCContext
    from smartcard.pcsc.PCSCExceptions import EstablishContextException
    try:
        PCSCContext().getContext()
    except EstablishContextException as e:
        log.error('Error while initializing pcsc: %s. Maybe pcscd is not installed on your system! ' +
                  'Yubikey storage disabled', str(e), exc_info=e)
    except Exception as e:
        log.error('Error while initializing pcsc: %s. Yubikey storage disabled',
                  str(e), exc_info=e)
    else:
        return _YubikeyFinder(settings)
