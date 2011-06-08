#!/usr/bin/env python3
import sys
import os
import socket
import ssl
import http.client
import xmlrpc.client
from optparse import OptionParser

APP_DESC = 'Performs operations on remote hosts using Viri'
APP_VERSION = '0.1'
DEFAULT_PORT = 6808
PROTOCOL = ssl.PROTOCOL_TLSv1

OPT_DATA = (('-d', '--data'), dict(dest='data',
    help='specifies that the operation is performed for data files',
    action='store_true', default=False))
OPT_OVERWRITE = (('-o', '--overwrite'), dict(dest='overwrite',
    help='overwrite the file if it exists on the remote host',
    action='store_true', default=False))
OPT_USE_ID = (('-i', '--use-id'), dict(dest='use_id',
    help='use script id instead of script file name',
    action='store_true', default=False))
OPT_VERBOSE = (('-v', '--verbose'), dict(dest='verbose',
    help='displays extended information',
    action='store_true', default=False))

CMD_DEF = {
    'execute': dict(
        desc='Executes a script in the remote host',
        args=(
            ('file_or_id', True),),
        options=(OPT_USE_ID,)),
    'put': dict(
        desc='Uploads a script or file to the remote host',
        args=(
            ('file', True),),
        options=(OPT_DATA,)),
    'ls': dict(
        desc='Lists remote scripts or files',
        args=[],
        options=(OPT_DATA, OPT_VERBOSE)),
    'get': dict(
        desc='Downloads a remote script or file',
        args=(
            ('filename_or_id', False),),
        options=(OPT_DATA, OPT_USE_ID),
        result=lambda x: x.data),
    'history': dict(
        desc='Displays script execution history',
        args=[],
        options=[]),
    'mv': dict(
        desc='Renames a file in the remote host',
        args=(
            ('source', False),
            ('destination', False)),
        options=(OPT_OVERWRITE,)),
    'rm': dict(
        desc='Removes a file in the remote host',
        args=(
            ('filename', False),),
        options=[]),
}

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

def main(cmd, kwargs):
    """Handles the connection to the remote virid server, and the execution of
    remote methods. All logic is implemented on the server, so if a invalid
    command is specified, the connection will be established. This makes this
    client generic, and changes to it are rarely required.
    """
    server = xmlrpc.client.ServerProxy(
        'https://%s:%s/' % (kwargs['host'], kwargs['port']),
        transport=TransportTLS(
            kwargs['keyfile'],
            kwargs['certfile'],
            use_datetime=False))

    del kwargs['host']
    del kwargs['port']
    del kwargs['keyfile']
    del kwargs['certfile']

    for (arg, is_file) in CMD_DEF[cmd]['args']:
        if is_file:
            kwargs['%s_name' % arg] = os.path.basename(kwargs[arg])
            with open(kwargs[arg], 'rb') as f:
                kwargs['%s_content' % arg] = xmlrpc.client.Binary(f.read())
            del kwargs[arg]

    return getattr(server, cmd)(kwargs)

def print_error(msg, cmd=None):
    program = sys.argv[0]
    sys.stderr.write('%s: %s\n' % (program, msg % dict(cmd=cmd)))
    sys.stderr.write('Try `%s help\' for more information.\n' % program)
    sys.exit(1)

def print_help(program):
    opts = 'Options:\n'
    for opt in parser.option_list:
        if len(opt._short_opts) > 0:
            short = ' (%s)' % opt._short_opts[0]
        else:
            short = ''
        if not isinstance(opt.default, tuple):
            default = ' (Default: %s)' % opt.default
        else:
            default = ''
        opts += '\t%s%s%s\n' % (
            ('%s%s' % (opt._long_opts[0], short)).ljust(20),
            opt.help, default)

    if len(sys.argv) > 2 and CMD_DEF.get(sys.argv[2]):
        help_cmd = CMD_DEF.get(sys.argv[2])
        sys.stdout.write(
            'Usage: %s %s %s [OPTIONS]\n\n' % (
                program, sys.argv[2],
                ' '.join([a[0] for a in help_cmd['args']])))
        sys.stdout.write('%s\n\n' % help_cmd['desc'])
        sys.stdout.write('%s\n' % opts)
        if help_cmd['options']:
            sys.stdout.write('Command options:\n')
            for cmd_opt in help_cmd['options']:
                sys.stdout.write('\t%s%s\n' % (
                ('%s (%s)' % (cmd_opt[0][1], cmd_opt[0][0])).ljust(20),
                cmd_opt[1]['help']))
    else:
        sys.stdout.write('Usage: %s COMMAND [OPTIONS]\n\n' % program)
        sys.stdout.write('Available commands:\n%s\n' %
            ''.join(['\t%s%s\n' % (key.ljust(12), val['desc'])
                for key, val in CMD_DEF.items()]))
        sys.stdout.write('%s\n' % opts)
            
        sys.stdout.write('See \'%s help COMMAND\' for more information '
            'on a specific command.\n' % program)

    sys.exit(0)

if __name__ == '__main__':
    parser = OptionParser(
        'Usage: %prog command [OPTIONS]',
        description=APP_DESC,
        version=APP_VERSION)
    parser.add_option('-H', '--host', dest='host',
        help='destination host', default='localhost')
    parser.add_option('-p', '--port', dest='port',
        help='destination port', type='int', default=DEFAULT_PORT)
    parser.add_option('-k', '--keyfile', dest='keyfile',
        help='TLS key')
    parser.add_option('-c', '--certfile', dest='certfile',
        help='TLS certificate', default='keys/viric.pem')

    if len(sys.argv) < 2:
        print_error('command argument is required')

    (program, cmd) = sys.argv[:2]
    program = os.path.basename(program)
    if cmd == 'help':
        print_help(program)

    if not CMD_DEF.get(cmd): 
        print_error('invalid command %(cmd)s', cmd)

    for opt in CMD_DEF[cmd]['options']:
        parser.add_option(*opt[0], **opt[1])
    (options, args) = parser.parse_args()

    if len(args) - 1 != len(CMD_DEF[cmd]['args']):
        print_error('invalid number of parameters for command %(cmd)s', cmd)

    params = dict(zip([arg[0] for arg in CMD_DEF[cmd]['args']], args[1:]))
    params.update(vars(options))
    try:
        (code, msg) = main(cmd, params)
    except Exception as exc:
        raise
        sys.stderr.write('%s\n' % str(exc))
        sys.exit(1)
    else:
        result_callback = CMD_DEF[cmd].get('result_callback')
        if result_callback:
            msg = result_callback(msg)
        sys.stdout.write('%s\n' % msg)
        try:
            code_int = int(code)
        except ValueError:
            sys.stderr.write(
                'Invalid response from the server: %s %s' % (code, msg))
            sys.exit(1)

