import sys
import socket
import ssl

if sys.version_info[0] == 2:
    import httplib as http_client
    import xmlrpclib as xmlrpc_client
else:
    from http import client as http_client
    from xmlrpc import client as xmlrpc_client

PROTOCOL = ssl.PROTOCOL_TLSv1

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


class Viric:
    def __init__(self, host, port, cert_file, key_file):
        self.server = xmlrpc_client.ServerProxy(
            'https://%s:%s/' % (host, port),
            transport=TransportTLS(
                key_file,
                cert_file,
                use_datetime=False))

    def __getattr__(self, attr):
        return getattr(self.server, attr)

