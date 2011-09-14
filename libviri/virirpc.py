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

    class XMLRPCRequestHandler(SimpleXMLRPCRequestHandler):    
        def handle(self):
            self.cert = self.request.getpeercert()
            super(SimpleXMLRPCRequestHandler, self).handle()

        def do_POST(self):
            """Handles the HTTP POST request.

            Attempts to interpret all HTTP POST requests as XML-RPC calls,
            which are forwarded to the server's _dispatch method for handling.
            """

            # Check that the path is legal
            if not self.is_rpc_path_valid():
                self.report_404()
                return
    
            try:
                # Get arguments by reading body of request.
                # We read this in chunks to avoid straining
                # socket.read(); around the 10 or 15Mb mark, some platforms
                # begin to have problems (bug #792570).
                max_chunk_size = 10*1024*1024
                size_remaining = int(self.headers["content-length"])
                L = []
                while size_remaining:
                    chunk_size = min(size_remaining, max_chunk_size)
                    L.append(self.rfile.read(chunk_size))
                    size_remaining -= len(L[-1])
                data = b''.join(L)
    
                data = self.decode_request_content(data)
                if data is None:
                    return #response has been sent

                # Add the certificate information into the XMLRPCRequest
                # as a parameter of the function. Blame Jesus.
                xml = xmlrpc_client.loads(data)
                function_name = xml[1]
                arguments = list(xml[0])
                arguments.append(self.cert)
                arguments = tuple(arguments)
                data = xmlrpc_client.dumps(arguments, function_name)
    
                # In previous versions of SimpleXMLRPCServer, _dispatch
                # could be overridden in this class, instead of in
                # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
                # check to see if a subclass implements _dispatch and dispatch
                # using that method if present.
                response = self.server._marshaled_dispatch(
                        data, getattr(self, '_dispatch', None), self.path
                    )
            except Exception as e: # This should only happen if the module is buggy
                # internal error, report as HTTP server error
                self.send_response(500)
    
                # Send information about the exception if requested
                if hasattr(self.server, '_send_traceback_header') and \
                        self.server._send_traceback_header:
                    self.send_header("X-exception", str(e))
                    trace = traceback.format_exc()
                    trace = str(trace.encode('ASCII', 'backslashreplace'), 'ASCII')
                    self.send_header("X-traceback", trace)
    
                self.send_header("Content-length", "0")
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/xml")
                if self.encode_threshold is not None:
                    if len(response) > self.encode_threshold:
                        q = self.accept_encodings().get("gzip", 0)
                        if q:
                            try:
                                response = gzip_encode(response)
                                self.send_header("Content-Encoding", "gzip")
                            except NotImplementedError:
                                pass
                self.send_header("Content-length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)
        
    class XMLRPCServer(SimpleXMLRPCServer):
        """Overriding standard xmlrpc.server.SimpleXMLRPCServer to run over TLS.
        Changes inspired by
        http://www.cs.technion.ac.il/~danken/SecureXMLRPCServer.py
        """
        def __init__(self, addr, ca_file, cert_key_file,
            requestHandler=XMLRPCRequestHandler, logRequests=True,
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
            cert_reqs=ssl.CERT_REQUIRED, ssl_version=PROTOCOL)


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

