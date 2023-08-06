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
Utilities to format TOTP/HOTP codes in an human readable way.
"""

import typing


formatter_type = typing.Callable[[int], str]
"""Type of a formatter method."""


def new_default_formatter(digits: int=6) -> formatter_type:
    """
    Returns a method that computes the stringified version of an HOTP/TOTP code using digits, left-padded with 0 to
    reach the requested number of digits.
    :param digits: number of requested digits.
    :return: formatter method.
    """
    def format_code(hotp: int) -> str:
        return '{:0{digits}d}'.format(hotp, digits=digits)
    return format_code


def new_steam_formatter() -> formatter_type:
    """
    Returns a method that computes the stringified version of an HOTP/TOTP in steam expected format.
    :return: formatter method.
    """
    steam_alphabet = '23456789BCDFGHJKMNPQRTVWXY'
    base = len(steam_alphabet)

    def format_code(hotp: int) -> str:
        chars = []
        for i in range(5):
            hotp, mod = divmod(hotp, base)
            chars.append(steam_alphabet[mod])
        return ''.join(chars)

    return format_code


def new_human_formatter(digits: int=6) -> formatter_type:
    """
    Formats the code by blocks of 3 or 4 characters, making them simpler
    to retain.

    :param digits:
    :return:

    >>> f = new_human_formatter(digits=8)
    >>> f(12345678)
    '1234 5678'
    >>> f(1234567)
    '0123 4567'
    >>> f = new_human_formatter()
    >>> f(12345678)
    '1234 5678'
    >>> f(1234567)
    '123 4567'
    >>> f(123456)
    '123 456'
    >>> f(12345)
    '012 345'
    """
    def format_code(hotp: int) -> str:
        s = '{:0{digits}d}'.format(hotp, digits=digits)

        length = len(s)
        if length < 4:
            return s

        sep = 4
        if length % 4 != 0 and length % 3 == 0:
            sep = 3

        splitted = [s[max(0, i - sep):i] for i in range(length, 0, -sep)]
        return ' '.join(reversed(splitted))

    return format_code
