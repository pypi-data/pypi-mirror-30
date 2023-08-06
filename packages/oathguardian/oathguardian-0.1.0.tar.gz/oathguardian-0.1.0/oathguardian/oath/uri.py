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
Parses key URI, as specified in
https://github.com/google/google-authenticator/wiki/Key-Uri-Format.
"""

import logging
import typing

from urllib.parse import urlsplit, parse_qs, unquote

log = logging.getLogger(__name__)

_DEFAULTS = {
    'algorithm': 'SHA1',
    'digits': 6,
    'period': 30,
}


def normalize_name(label: str, issuer: str=None) -> typing.Tuple[str, typing.Optional[str]]:
    """Ensures there is no redundancy between label and issuer, as labels generally are prefixed with issuer
    and a colon.

    >>> normalize_name('Amazon:ham@spam.org', 'Amazon')
    ('ham@spam.org', 'Amazon')
    >>> normalize_name('Amazon:ham@spam.org')
    ('ham@spam.org', 'Amazon')
    >>> normalize_name('ham@spam.org')
    ('ham@spam.org', None)
    """
    if not issuer:
        head, sep, tail = label.partition(':')
        if tail:
            return tail, head
        return head, None

    if label.startswith(issuer + ':'):
        label = label[len(issuer) + 1:]
    return label, issuer


def parse_uri(url: str) -> dict:
    """Parses the given otpauth URI into a dictionary. The resulting dictionary will have the
    following entries:

    - oath_type (str): totp or hotp (mandatory),
    - label (str): the label, generally an account name (mandatory),
    - secret (str): the key, as a b32 encoding string (mandatory),
    - issuer (str): the issuer, generally the website name,
    - algorithm (str): the hash algorithm to use (mandatory),
    - digits (int): the number of digits the resulting code must keep (mandatory),
    - counter (int): the initial counter for hotp credentials (mandatory for hotp),
    - periodr (int): the period for totp credentials (mandatory for totp),

    :param url: the uri to parse
    :return: all parameters as a dictionary.
    """
    split = urlsplit(url)
    log.info(split)
    query = parse_qs(split.query)

    label = unquote(split.path[1:])
    issuer = query.get('issuer', [None])[0]

    label, issuer = normalize_name(label, issuer)

    res = {
        'oath_type': split.netloc,
        'label': label,
        'secret': query['secret'][0],
        'issuer': issuer,
    }

    for optional in ('algorithm', 'digits', 'counter', 'period'):
        if optional in query:
            res[optional] = query[optional][0]
        elif optional in _DEFAULTS:
            res[optional] = _DEFAULTS[optional]

    log.debug('Parsed %s into %s', url, res)

    return res
