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

import base64
import typing

key_types = typing.Union[str, bytes, bytearray]
"""Accepted types for key in generate_totp, generate_hotp methods. str means 'b32 encoded'."""


def b32_normalize(key: str) -> str:
    """
    Web sites often gives the secret with spaces between 4-char words. This method normalizes
    the received key into one parseable by base64, and handles padding.

    :param key: the original key.
    :return: a normalized b32 string.
    """
    # This piece of really clever code was taken from ykman.util.parse_b32_key
    key = key.upper().replace(' ', '')
    # if key length is not a multiple of 8, pad with '=' chars.
    key += '=' * (-len(key) % 8)
    return key


def to_binary_key(key: key_types) -> bytes:
    """
    Converts a key to its bytes representation.

    :param key: a key, either as a base32 encoded string, or a byte array.
    :return: the binary key.
    """
    if isinstance(key, base64.bytes_types):
        return key
    else:
        return base64.b32decode(b32_normalize(key))


def to_b32_key(key: key_types) -> str:
    """
    Converts a key to its string representation, in base32.

    :param key: a key, either as a base32 encoded string, or a byte array.
    :return: the base32 encoded key.
    """
    if isinstance(key, base64.bytes_types):
        return base64.b32encode(key).decode('ascii')
    return b32_normalize(key)
