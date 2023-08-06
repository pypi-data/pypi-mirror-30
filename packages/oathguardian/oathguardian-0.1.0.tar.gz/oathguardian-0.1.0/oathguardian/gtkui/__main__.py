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

import gettext
import logging
import logging.config
import os
import signal
import sys

from gi.repository import GLib
from gi.repository import Gtk

import oathguardian
from .application import OathGuardian

log = logging.getLogger(__name__)


def main():
    logging_conf = os.path.expanduser('~/.config/oathguardian/logging.conf')
    if os.path.exists(logging_conf):
        logging.config.fileConfig(logging_conf)
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)-15s [%(threadName)-16s] %(levelname)s %(name)s: %(message)s')

    name = oathguardian.NAME

    log.info('Starting %s v%s', name, oathguardian.VERSION)

    gettext.bindtextdomain('oathguardian',
                           [os.path.join(sys.prefix, 'share', 'locale')])
    gettext.textdomain('oathguardian')

    if hasattr(GLib, "unix_signal_add"):
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT,
                             Gtk.main_quit, None)
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM,
                             Gtk.main_quit, None)

    app = OathGuardian()
    app.run(sys.argv)

    log.info('Stopping %s', name)


if __name__ == '__main__':
    main()
