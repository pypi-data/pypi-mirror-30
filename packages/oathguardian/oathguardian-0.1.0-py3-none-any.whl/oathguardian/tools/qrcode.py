# coding: utf-8

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

try:
    from pyzbar import pyzbar
    from PIL import Image
    decoding_supported = True
except:
    decoding_supported = False

from oathguardian import oath

log = logging.getLogger(__name__)

_DEFAULTS = {
    'algorithm': 'SHA1',
    'digits': 6,
    'period': 30,
}


def decode(filename):
    with Image.open(filename) as image:
        data = pyzbar.decode(image)

    if not data:
        return {}

    decoded = data[0]
    if 'QRCODE' != decoded.type:
        return {}

    url = decoded.data.decode('utf-8')

    log.debug('Decoded %s', url)

    return oath.parse_uri(url)
