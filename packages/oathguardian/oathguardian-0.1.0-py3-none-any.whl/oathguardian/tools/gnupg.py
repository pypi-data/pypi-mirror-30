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
Tools for talking talk to gpg tools (gpg-agent and pinentry).
"""

import contextlib
import logging
import io
import os
import re
import socket
import subprocess
import typing

log = logging.getLogger(__name__)


_MAPPING = (('\n', '%0A'), ('\r', '%0D'), ('%', '%25'))


class AssuanError(Exception):
    """
    Error raised when a command sent to gpg-agent or pinentry returned with an error.
    """
    ERROR_PATTERN = re.compile('(?P<errorcode>\d+) (?P<message>.*)')

    def __init__(self, line):
        self.code, self.message = self._parse(line)

    @classmethod
    def _parse(cls, line: str):
        m = cls.ERROR_PATTERN.match(line)
        if m:
            return int(m.group('errorcode')), m.group('message')
        return 0, line


class AssuanProtocolError(Exception):
    """

    """
    pass


class Assuan(object):
    """
    A base class for sending commands and receiving responses to a process supporting
    an assuan protocol.
    """
    MAX_LINE_LENGTH = 1000
    RESPONSE_PATTERN = re.compile('^(?P<type>D|S|#|OK|ERR)(?:\s+(?P<data>.*))?$')

    def __init__(self, name, reader, writer):
        self.name = name
        self.input = reader
        self.output = writer
        self._log = logging.getLogger('{module}.{cls}.{cls}-{name}'.format(module=__name__,
                                                                           cls=Assuan.__name__,
                                                                           name=name))
        self._readline()

    def _log_input(self, line):
        self._log.info('<<< %s', line)

    def _log_output(self, line):
        self._log.info('>>> %s', line)

    def _readline(self, log_data: bool=True) -> typing.Tuple[str, str]:
        line = self.input.readline()
        if not line:
            raise AssuanProtocolError('EOF')

        line = line.rstrip()

        if len(line) > self.MAX_LINE_LENGTH:
            self._log_input(line)
            raise AssuanProtocolError('line too long')

        matcher = self.RESPONSE_PATTERN.match(line)
        if not matcher:
            raise AssuanProtocolError('Invalid response {}'.format(line))

        msg_type = matcher.group('type')
        if msg_type == 'D' and not log_data:
            self._log_input('D <hidden_data>')
        else:
            self._log_input(line)

        return msg_type, matcher.group('data') or ''

    def _responses(self, log_data: bool=True) -> typing.Generator[typing.Tuple[str, str], None, None]:
        while True:
            resp_type, resp_data = self._readline(log_data=log_data)
            if resp_type == '#':
                continue
            yield resp_type, self._decode(resp_data)
            if resp_type in ('OK', 'ERR'):
                return

    @staticmethod
    def _encode(s: str):
        tr = str.maketrans({decoded: encoded for decoded, encoded in _MAPPING})
        return s.translate(tr)

    @staticmethod
    def _decode(s: str):
        # Cannot use translate here as encoded is more than 1 char
        mapping = {encoded: decoded for decoded, encoded in _MAPPING}
        pattern = re.compile('|'.join(encoded for _, encoded in _MAPPING))
        return pattern.sub(lambda m: mapping.get(m.group(0), ''), s)

    def set_option(self, name, value=None):
        """
        Set the given option, with potential value.

        This is a shortcut to sending command SETOPTION name value.

        :param name: name of the option to set.
        :param value: optional value for the option
        :return:
        """
        args = [name]
        if value:
            args.append(str(value))
        return self.send('OPTION', args)

    def send(self, cmd, args=None, log_data=True):
        """
        Sends the given command, with optional arguments.

        :param str cmd: the command (eg. GETPIN, SETKEYINFO, etc.)
        :param iterable[str] args: command arguments.
        :param bool log_data: if False, the data in response won't be logged.
        :return:
        """
        if args is None:
            args = []

        command = cmd + ' ' + ' '.join(self._encode(x) for x in args) + '\n'

        self._log_output(command[:-1])

        self.output.write(command)
        self.output.flush()

        responses = list(self._responses(log_data=log_data))
        if responses[-1][0] == 'ERR':
            raise AssuanError(responses[-1][1])

        data = ''.join(r[1] for r in responses[:-1] if r[0] == 'D')
        return data, responses[-1]

    def bye(self):
        try:
            self.send('BYE')
        except (AssuanError, AssuanProtocolError) as e:
            log.error('Error while taking leave of %s: %s', self.name, str(e), exc_info=e)


@contextlib.contextmanager
def gpg_agent(socket_path: str) -> Assuan:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(socket_path)
        with s.makefile(mode='rw', encoding='utf-8', newline='\n') as fd:
            agent = Assuan('gpg-agent', fd, fd)
            try:
                yield agent
            finally:
                agent.bye()


class PinEntry(Assuan):
    """
    Helper for using pinentry to ask passwords to user.
    """
    def __init__(self, name, reader, writer):
        super().__init__(name, reader, writer)

    def set_keyinfo(self, keygrip):
        self.send('SETKEYINFO ', args=[keygrip])

    def set_error(self, errmsg='Invalid PIN.'):
        self.send('SETERROR', args=[errmsg])

    def ask_pin(self, prompt='PIN:'):
        self.send('SETPROMPT', args=[prompt])
        data, _ = self.send('GETPIN', log_data=False)
        return data


@contextlib.contextmanager
def pinentry(executable='pinentry'):

    def iowrap(rawio):
        return io.TextIOWrapper(rawio, encoding='utf-8', newline='\n')

    with subprocess.Popen([], executable=executable, stdout=subprocess.PIPE, stdin=subprocess.PIPE) as process:
        with iowrap(process.stdin) as writer, iowrap(process.stdout) as reader:
            pin_entry = PinEntry('pinentry', reader, writer)
            try:
                yield pin_entry
            finally:
                pin_entry.bye()


def kill_scdaemon(socket_path: str=None) -> bool:
    """
    Sends the SCD RESTART and SCD BYE commands to the gpg agent via the given socket. This makes the scdaemon
    to quit, allowing to use a yubikey otherwise used with gpg.
    :param socket_path: control socket for scdaemon.
    :return: True if the calls succeed, False otherwise
    """
    if socket_path is None:
        socket_path = '/run/user/{uid}/gnupg/S.gpg-agent'.format(uid=os.getuid())

    if not os.path.exists(socket_path):
        log.info('Could not kill scdaemon as gpg-agent socket path %s was not found!', socket_path)
        return False

    log.info('Killing scdaemon using socket %s', socket_path)

    with gpg_agent(socket_path) as agent:
        try:
            agent.send('SCD RESTART')
            agent.send('SCD BYE')
        except AssuanError as e:
            log.error('Unable to kill scdaemon: 0x%x %s', e.code, e.message, exc_info=e)
            return False

    return True
