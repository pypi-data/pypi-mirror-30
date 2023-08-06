# coding: utf-8

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


"""

"""

import configparser
import logging
import os

log = logging.getLogger(__name__)


class Config(object):
    def __init__(self):
        self._config = configparser.ConfigParser()

    def load_config(self):
        filename = os.path.expanduser('~/.config/oathguardian/oathguardian.conf')
        if os.path.exists(filename):
            log.info('Loading configuration from %s', filename)
            self._config.read(filenames=[filename], encoding='utf-8')

    def gpg_agent_path(self):
        default_path = '/run/user/{uid}/gnupg/S.gpg-agent'.format(uid=os.getuid())
        if 'gnupg' in self._config:
            return self._config['gnupg'].get('gpg_agent_path', default_path)
        return default_path

    def pinentry_executable(self):
        default_executable = 'pinentry'
        if 'gnupg' in self._config:
            return self._config['gnupg'].get('pinentry', default_executable)
        return default_executable
