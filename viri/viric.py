import sys
import os
import socket
import ssl
import http.client
import xmlrpc.client
from optparse import OptionParser

APP_NAME = 'viric'
APP_DESC = 'Sends tasks to be executed in virid instances'
APP_VERSION = '0.0.1'
DEFAULT_PORT = 6808
PROTOCOL = ssl.PROTOCOL_TLSv1
BASE_USAGE = 'Usage: %prog [OPTIONS]'
COMMANDS = {
    'send_task': 'FILENAME',
    'send_exec_task': 'FILENAME',
    'send_data': 'FILENAME',
    'exec_task': 'TASK'}


class HTTPConnectionTLS(http.client.HTTPSConnection):
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


class TransportTLS(xmlrpc.client.Transport):
    """Extending xmlrpc.client.Transport class, so we can specify client
    certificates needed for client authentication.
    """
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
        headers['Content-Type'] = 'text/xml'
        headers['User-Agent'] = self.user_agent
        connection.request('POST', handler, request_body, headers)
        return connection


class UsageError(Exception):
    """Custom exception representing the error raised when a user
    is using the program with wrong options or arguments
    """
    pass


class ViriClient:
    """
    """
    def __init__(self, host, port, keyfile, certfile, **kwargs):
        self.server = xmlrpc.client.ServerProxy(
            'https://%s:%s/' % (host, port),
            transport=TransportTLS(
                keyfile,
                certfile,
                use_datetime=False))

    def _parse_result(self, result):
        (code, msg) = result.split(' ', 1)
        return msg

    def _is_python_file(self, filename):
        return filename.split('.')[-1] in ('py', 'pyc', 'pyo')

    def send_task(self, filename):
        with open(filename, 'rb') as f:
            result = self.server.send_task(
                os.path.split(filename)[1],
                xmlrpc.client.Binary(f.read()))
        return self._parse_result(result)

    def send_data(self, filename, overwrite):
        with open(filename, 'rb') as f:
            result = self.server.send_data(
                os.path.split(filename)[1],
                xmlrpc.client.Binary(f.read()),
                overwrite)
        return self._parse_result(result)

    def exec_task(self, task_id):
        result = self.server.exec_task(task_id)
        return self._parse_result(result)

    def exec_command(self, cmd, *args, **options):
        if len(args) != len(COMMANDS[cmd].split(' ')):
            raise UsageError('Invalid number of arguments')

        if cmd in ('send_exec_task', 'send_task') and \
            not self._is_python_file(args[0]):
            raise UsageError('Script file must be a Python file')

        if cmd == 'send_task':
            return self.send_task(args[0])
        elif cmd == 'send_exec_task':
            task_id = self.send_task(args[0])
            return self.exec_task(task_id)
        elif cmd == 'send_data':
            return self.send_data(args[0], options['overwrite'])
        elif cmd == 'exec_task':
            return self.exec_task(args[0])


if __name__ == '__main__':
    parser = OptionParser(
        BASE_USAGE + ' command',
        description=APP_DESC,
        version=APP_VERSION)
    parser.add_option('--host', dest='host',
        help='destination host', default='localhost')
    parser.add_option('-p', '--port', dest='port',
        help='destination port', type='int', default=DEFAULT_PORT)
    parser.add_option('-k', '--keyfile', dest='keyfile',
        help='TLS key')
    parser.add_option('-c', '--certfile', dest='certfile',
        help='TLS certificate', default='keys/viric.pem')
    parser.add_option('-o', '--overwrite', dest='overwrite',
        help='destination port', action='store_true', default=False)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error('Command argument is required')
    elif args[0] not in COMMANDS.keys():
        parser.error('%s is not a %s command' % (
            args[0], APP_NAME))
    else:
        parser.set_usage(BASE_USAGE + ' %s %s' % (args[0], COMMANDS[args[0]]))

    viric = ViriClient(**vars(options))
    try:
        result = viric.exec_command(*args, **vars(options))
    except UsageError as exc:
        parser.error('%s\n' % str(exc))
    except Exception as exc:
        sys.stderr.write('%s\n' % str(exc))
        sys.exit(1)
    else:
        sys.stdout.write('%s\n' % result)

