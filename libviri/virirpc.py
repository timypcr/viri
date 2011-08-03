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

import sys
import ssl
import socket

PROTOCOL = ssl.PROTOCOL_TLSv1

# This file works in both Python 2 (>= 2.6) and Python 3
if sys.version_info[0] == 2:
    import httplib as http_client
    import xmlrpclib as xmlrpc_client
else:
    from http import client as http_client
    from xmlrpc import client as xmlrpc_client
    from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, \
        SimpleXMLRPCRequestHandler

    class XMLRPCServer(SimpleXMLRPCServer):
        """Overriding standard xmlrpc.server.SimpleXMLRPCServer to run over TLS.
        Changes inspired by
        http://www.cs.technion.ac.il/~danken/SecureXMLRPCServer.py
        """
        def __init__(self, addr, ca_file, cert_key_file,
            requestHandler=SimpleXMLRPCRequestHandler, logRequests=True,
            allow_none=False, encoding=None, bind_and_activate=True):
            """Overriding __init__ method of the SimpleXMLRPCServer

            The method is a copy, except for the TCPServer __init__
            call, which is rewritten using TLS, and the certfile argument
            which is required for TLS
            """
            import socketserver

            self.logRequests = logRequests
            SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)
            socketserver.BaseServer.__init__(self, addr, requestHandler)
            self.socket = ssl.wrap_socket(
                socket.socket(self.address_family, self.socket_type),
                server_side=True,
                certfile=cert_key_file,
                ca_certs=ca_file,
                cert_reqs=ssl.CERT_REQUIRED,
                ssl_version=PROTOCOL)
            if bind_and_activate:
                self.server_bind()
                self.server_activate()

            # [Bug #1222790] If possible, set close-on-exec flag; if a
            # method spawns a subprocess, the subprocess shouldn't have
            # the listening socket open.
            try:
                import fcntl
            except ImportError:
                pass
            else:
                if hasattr(fcntl, 'FD_CLOEXEC'):
                    flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
                    flags |= fcntl.FD_CLOEXEC
                    fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)


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


class XMLRPCClient:
    def __init__(self, url, key_file, cert_file):
        self.server = xmlrpc_client.ServerProxy(
            url,
            transport=TransportTLS(
                key_file,
                cert_file,
                use_datetime=True),
            allow_none=True)

    def __getattr__(self, attr):
        return getattr(self.server, attr)


Binary = xmlrpc_client.Binary

