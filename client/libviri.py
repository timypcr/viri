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
import socket
import ssl
from optparse import OptionParser

if sys.version_info[0] == 2:
    import httplib as http_client
    import xmlrpclib as xmlrpc_client
else:
    from http import client as http_client
    from xmlrpc import client as xmlrpc_client

PROTOCOL = ssl.PROTOCOL_TLSv1
DEFAULT_PORT = 6808

class HTTPConnectionTLS(http_client.HTTPSConnection):
    """Extending http.client.HTTPSConnection class, so we can specify which
    protocol we want to use (we'll use TLS instead SSL)
    """
    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
            ssl_version=PROTOCOL)


class TransportTLS(xmlrpc_client.Transport, object):
    """Extending xmlrpc.client.Transport class, so we can specify client
    certificates needed for client authentication.
    """
    def __init__(self, key_file, cert_file, *args, **kwargs):
        self.key_file = key_file
        self.cert_file = cert_file
        super(TransportTLS, self).__init__(*args, **kwargs)

    def request(self, host, handler, request_body, verbose=False):
        host, extra_headers, x509 = self.get_host_info(host)
        http_conn = HTTPConnectionTLS(
            host,
            None,
            self.key_file,
            self.cert_file,
            **(x509 or {}))
        headers = {}
        if extra_headers:
            for key, val in extra_headers:
                headers[key] = val
        headers['Content-Type'] = 'text/xml'
        headers['User-Agent'] = self.user_agent
        http_conn.request('POST', handler, request_body, headers)
        resp = http_conn.getresponse()

        if resp.status != 200:
            raise xmlrpc_client.ProtocolError(
                host + handler,
                resp.status, resp.reason,
                dict(resp.getheaders()))

        self.verbose = verbose
        return self.parse_response(resp)


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
        return xmlrpc_client.ServerProxy(
            'https://{0}/'.format(self.current_host),
            transport=TransportTLS(
                self.key_file,
                self.cert_file,
                use_datetime=False))

    def _get_file_content(self, filename):
        with open(filename, 'rb') as f:
            return xmlrpc_client.Binary(f.read())

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

