"""Monkey patching standard xmlrpc.server.SimpleXMLRPCServer
to run over TLS (SSL)

Changes inspired on http://www.cs.technion.ac.il/~danken/SecureXMLRPCServer.py
"""
import socket
import socketserver
import ssl
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, SimpleXMLRPCRequestHandler
try:
    import fcntl
except ImportError:
    fcntl = None

PROTOCOL = ssl.PROTOCOL_TLSv1

class SimpleXMLRPCServerTLS(SimpleXMLRPCServer):
    def __init__(self, addr, certfile, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=True, allow_none=False, encoding=None, bind_and_activate=True):
        """Overriding __init__ method of the SimpleXMLRPCServer

        The method is an exact copy, except for the TCPServer __init__
        call, which is rewritten using TLS, and the certfile argument
        which is required for TLS
        """
        self.logRequests = logRequests

        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)

        """This is the modified part. Original code was:

            socketserver.TCPServer.__init__(self, addr, requestHandler, bind_and_activate)

        which executed:

            def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
                BaseServer.__init__(self, server_address, RequestHandlerClass)
                self.socket = socket.socket(self.address_family,
                                            self.socket_type)
                if bind_and_activate:
                    self.server_bind()
                    self.server_activate()

        """
        socketserver.BaseServer.__init__(self, addr, requestHandler)
        self.socket = ssl.wrap_socket(
            socket.socket(self.address_family, self.socket_type),
            server_side=True,
            certfile=certfile,
            cert_reqs=ssl.CERT_NONE,
            ssl_version=PROTOCOL,
            )
        if bind_and_activate:
            self.server_bind()
            self.server_activate()

        """End of modified part"""

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        if fcntl is not None and hasattr(fcntl, 'FD_CLOEXEC'):
            flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)


"""Monkey patching standard http.client library, to let
xmlrpc.client.ServerProxy use TLSv1 instead of SSLv2, and
to be able to specify the certificate, and other SSL/TLS options
"""

from xmlrpc.client import Transport
from http.client import HTTPConnection, HTTPSConnection


class HTTPConnectionTLS(HTTPSConnection):
    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        HTTPConnection.__init__(self, host, port, strict, timeout)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        sock = socket.create_connection((self.host, self.port), self.timeout)

        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
            ssl_version=PROTOCOL)


class TransportTLS(Transport):
    def __init__(self, key_file, cert_file, *args, **kwargs):
        self.key_file = key_file
        self.cert_file = cert_file
        super(TransportTLS, self).__init__(*args, **kwargs)

    def send_request(self, host, handler, request_body, debug):
        host, extra_headers, x509 = self.get_host_info(host)
        connection = HTTPConnectionTLS(
            host,
            None,
            self.key_file,
            self.cert_file,
            **(x509 or {}))
        if debug:
            connection.set_debuglevel(1)
        headers = {}
        if extra_headers:
            for key, val in extra_headers:
                headers[key] = val
        headers["Content-Type"] = "text/xml"
        headers["User-Agent"] = self.user_agent
        connection.request("POST", handler, request_body, headers)
        return connection

