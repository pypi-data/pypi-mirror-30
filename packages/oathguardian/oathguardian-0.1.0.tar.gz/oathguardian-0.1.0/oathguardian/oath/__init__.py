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

"""
Utilities for computing HOTP and TOTP codes.
"""

from .formatters import (formatter_type, new_default_formatter, new_human_formatter, new_steam_formatter)
from .keys import (key_types, to_binary_key, b32_normalize, to_b32_key)
from .oath import (generate_hotp, generate_totp)
from .providers import Provider, OATHType, HashAlgo, Credential, Code
from .uri import parse_uri
