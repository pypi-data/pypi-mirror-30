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

import abc
import enum
import functools
import typing

from collections import namedtuple

from ... import oath


@enum.unique
class OATHType(enum.Enum):
    """Algorithm types."""
    TOTP = 'totp'
    HOTP = 'hotp'


@enum.unique
class ProviderCapability(enum.IntFlag):
    TOTP = enum.auto()
    HOTP = enum.auto()
    LOCK = enum.auto()


@enum.unique
class HashAlgo(enum.Enum):
    """Supported hash algorithms."""
    SHA1 = 'sha1'
    SHA256 = 'sha256'
    SHA512 = 'sha512'


Code = namedtuple('Code', ['code', 'representation', 'digits', 'expiry', 'period'])
Code.__doc__ = """Result of a TOTP/HOTP computation.
:param int code: actual result.
:param int digits: number of digits required for code (for a formatter to properly pad with zeroes if needed).
:param int expiry: timestamp at which this code expires.
:param int period: validity duration of this code.
"""


@functools.total_ordering
class Credential(metaclass=abc.ABCMeta):
    """
    Object identifying a credential stored in a provider.
    """
    def __init__(self, name: str, issuer: str=None):
        self._name = name
        self._issuer = issuer

    @property
    @abc.abstractmethod
    def provider(self) -> 'Provider':
        pass

    @property
    def issuer(self) -> str:
        return self._issuer

    @property
    def name(self) -> str:
        return self._name

    @property
    @abc.abstractmethod
    def type(self) -> OATHType:
        pass

    def compute(self, **kwargs) -> Code:
        code, digits, expiry, period = self._compute0(**kwargs)
        formatter = kwargs.pop('formatter', oath.new_default_formatter(digits))
        return Code(code, formatter(code), digits, expiry, period)

    @abc.abstractmethod
    def _compute0(self, **kwargs) -> typing.Tuple[int, int, int, int]:
        raise NotImplementedError

    def __lt__(self, other):
        a = (self.issuer or '', self.name)
        b = (other.issuer or '', other.name)
        return a < b

    def __str__(self):
        return '{}:{}'.format(self.issuer or '', self.name)


class Provider(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def id(self) -> str:
        """Unique identifier for the provider. Preferred way to build this id is by using a pattern
        {provider_type}:{provider_key}.

        :return str: provider identifier.
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Display name
        :return str: display name
        """
        pass

    @property
    @abc.abstractmethod
    def capabilities(self) -> ProviderCapability:
        pass

    @abc.abstractmethod
    def list(self) -> typing.List[Credential]:
        pass

    @abc.abstractmethod
    def add(self, oath_type: OATHType, label: str, secret: oath.key_types,
            issuer: str=None, algorithm: HashAlgo=HashAlgo.SHA1, digits: int=6,
            counter: int=None, period: int=30, **kwargs) -> Credential:
        pass

    @abc.abstractmethod
    def remove(self, cred: Credential):
        """Removes the given credential from this storage.
        :param Credential cred: credential to remove.
        :throw ValueError: if the give credential i
        """
        pass

    @abc.abstractmethod
    def is_locked(self) -> bool:
        """Tells if the current storage is locked. If locked, a call to unlock method is required
        before being able to do any other operation of the storage.
        :return bool: True if this storage is locked.
        """
        pass

    @abc.abstractmethod
    def unlock(self) -> bool:
        pass
