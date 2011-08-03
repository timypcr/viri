# Copyright 2011, Marc Garcia <garcia.marc@gmail.com>
#
# This file is part of Viri.
#
# Viri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Viri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Viri.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from optparse import OptionParser
from libviri.virirpc import XMLRPCClient, Binary


DEFAULT_PORT = 6808


class ViriError(Exception):
    pass


class Viric(object):
    def __init__(self, hosts, cert_file, key_file):
        self.hosts = hosts
        self.cert_file = cert_file
        self.key_file = key_file
        self.current_host = self.hosts[0]

    @property
    def connection(self):
        return XMLRPCClient(
            'https://{0}/'.format(self.current_host),
            self.keyfile,
            self.certfile)

    def _get_file_content(self, filename):
        with open(filename, 'rb') as f:
            return Binary(f.read())

    def _handle_result(self, result):
        if not result[0]:
            return result[1]
        else:
            # TODO make the traceback available
            msg = '\n' + result[1]
            raise ViriError(msg)

    def execute(self, file_name_or_id, args=[]):
        res = self.connection.execute(dict(
            file_name_or_id=file_name_or_id,
            args=args))
        return self._handle_result(res)

    def put(self, filename):
        res = self.connection.put(dict(
            file_name=os.path.basename(filename),
            file_content=self._get_file_content(filename),
            execute=False,
            args=[]))
        return self._handle_result(res)

    def sched(self, filename_or_id, minute, hour, month_day, month, week_day,
        year, delete=False):
        res = self.connection.sched(dict(
            filename_or_id=filename_or_id,
            cron_def=' '.join((
                minute,
                hour,
                month_day,
                month,
                week_day,
                year)),
            delete=delete))
        return self._handle_result(res)

    def ls(self, sched):
        res = self.connection.ls(dict(
            sched=sched))
        return self._handle_result(res)

    def get(self, file_name_or_id):
        res = self.connection.get(dict(
            file_name_or_id=file_name_or_id))
        return self._handle_result(res)

    def history(self):
        res = self.connection.get({})
        return self._handle_result(res)


class ArgsViric(Viric):
    def __init__(self):
        parser = OptionParser()
        parser.add_option('-H', '--hosts', dest='hosts', default='localhost')
        parser.add_option('-k', '--keyfile', dest='keyfile', default=None)
        parser.add_option('-c', '--certfile', dest='certfile',
            default=os.path.expanduser('~/.viri/viric.pem'))
        (options, self.args) = parser.parse_args()

        hosts = list(map(
            lambda x: x if ':' in x else ':'.join((x, str(DEFAULT_PORT))),
            options.hosts.split(',')))

        super(ArgsViric, self).__init__(hosts, options.certfile, options.keyfile)

    def run(self, host=None):
        # TODO capture and send command line args
        if host:
            self.current_host = host
        script = os.path.abspath(sys.modules['__main__'].__file__)
        script_id = self.put(script)
        self.execute(script_id, self.args)

viric = ArgsViric()

