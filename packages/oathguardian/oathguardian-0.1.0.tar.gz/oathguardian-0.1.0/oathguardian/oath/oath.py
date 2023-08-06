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
import hmac
import time
import logging

from .keys import (key_types, b32_normalize)


def generate_hotp(key: key_types, counter: int, digits: int=6, hash_algo: str='sha1') -> int:
    """
    Generates an HOTP code following RFC 4226. The returned value is an int, that has to be formatted.

    Indeed, some issuers are not expecting the HOTP code to be formatted as documented (eg. steam).

    :param key: the key, either as a b32 string or a byte array.
    :param counter: the counter.
    :param digits: required number of digits, generally 6 or 8
    :param hash_algo: hash algorithm to use. For HOTP code it is sha1, as RFC 4226 is pretty strict about it. However,
                      for TOTP codes, sha256 or sha512 may be used.
    :return: the HOTP code, as int.
    """
    if counter < 0:
        raise ValueError('Counter must be positive')

    log = logging.getLogger(__name__)

    log.debug('Generating HOTP for counter=%d with key=%s, digits=%d, algo=%s', counter, key, digits, hash_algo)

    if isinstance(key, base64.bytes_types):
        key_bytes = key
    else:
        key_bytes = base64.b32decode(b32_normalize(key))

    counter_bytes = counter.to_bytes(8, byteorder='big')

    # gets the HMAC-SHA1 value of counter_bytes by key
    hmac_result = hmac.new(key_bytes, counter_bytes, digestmod=hash_algo).digest()

    # directly copied from https://www.ietf.org/rfc/rfc4226.txt section 5.4
    offset = hmac_result[-1] & 0xf
    bin_code = ((hmac_result[offset] & 0x7f) << 24
                | (hmac_result[offset+1] & 0xff) << 16
                | (hmac_result[offset+2] & 0xff) << 8
                | (hmac_result[offset+3] & 0xff))

    return bin_code % (10 ** digits)


def generate_totp(key: key_types, timestamp: int=None, period: int=30,
                  digits: int=6, hash_algo: str='sha1', origin: int=0) -> int:
    """
    Generates an TOTP code following RFC 6238. In fact, this is just computing an HOTP code by using
    ``(timestamp - origin) // period`` as counter.

    :param key: the key, either formatted as a b32 string or in binary.
    :param timestamp: the timestamp in seconds for which to compute the token. If not provided, current time will be
                      taken.
    :param period: time step in seconds.
    :param digits: required number of digits, generally 6 or 8
    :param hash_algo: hash algorithm to use. For HOTP code it is sha1, as RFC 4226 is pretty strict about it. However,
                      for TOTP codes, sha256 or sha512 may be used.
    :param origin: Unix time (in seconds) to start counting steps. Default is 0 (the Epoch).
    :return: the HOTP code, as int.
    """
    if timestamp is None:
        timestamp = int(time.time())

    steps = (timestamp - origin) // period

    return generate_hotp(key, steps, digits=digits, hash_algo=hash_algo)
