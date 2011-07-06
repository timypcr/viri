import sys
import socket
import ssl

PY3 = sys.version_info[0] == 3

if PY3:
    from http import client as http_client
    from xmlrpc import client as xmlrpc_client
else:
    import httplib as http_client
    import xmlrpclib as xmlrpc_client

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

    def request_py2(self, host, handler, request_body, extra_headers, x509):
        http_conn = http_client.HTTPS(host, None, **(x509 or {}))
        http_conn.putrequest("POST", handler)
        self.send_host(http_conn, host)
        self.send_user_agent(http_conn)
        self.send_content(http_conn, request_body)

        errcode, errmsg, headers = http_conn.getreply()

        if errcode != 200:
            raise xmlrpc_client.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        try:
            sock = http_conn._conn.sock
        except AttributeError:
            sock = None

        return self._parse_response(http_conn.getfile(), sock)

    def request_py3(self, host, handler, request_body, extra_headers, x509):
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
                dict(resp.getheaders())
                )

        return self.parse_response(resp)

    def request(self, host, handler, request_body, verbose=False):
        host, extra_headers, x509 = self.get_host_info(host)
        self.verbose = verbose
        if True:
            return self.request_py3(
                host, handler, request_body, extra_headers, x509)
        else:
            return self.request_py2(
                host, handler, request_body, extra_headers, x509)


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

