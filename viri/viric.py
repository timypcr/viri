import sys
import os
import binascii
import xmlrpc.client
from optparse import OptionParser
import settings

BASE_USAGE = 'Usage: %prog [OPTIONS]'
COMMANDS = {
    'send_task': 'FILENAME',
    'send_exec_task': 'FILENAME',
    'send_data': 'FILENAME',
    'exec_task': 'TASK'}


class UsageError(Exception):
    pass


class RSAError(Exception):
    pass


class SignRSA:
    def __init__(self, key_filename):
        self.key = self._load_key(key_filename)

    def _load_key(self, filename):
        START_LINE = '-----BEGIN RSA PRIVATE KEY-----'
        END_LINE = '-----END RSA PRIVATE KEY-----'
        BEFORE_KEY = -1
        IN_KEY = 0
        AFTER_KEY = 1

        if not os.path.isfile(filename):
            raise RSAError('File not found: %s' % filename)

        position = BEFORE_KEY
        key = ''
        with open(filename, 'r') as f:
            for line in f.readlines():
                if position == IN_KEY:
                    if END_LINE in line:
                        position = AFTER_KEY
                        break
                    else:
                        key += line.strip()
                elif position == BEFORE_KEY and START_LINE in line:
                    position = IN_KEY

        if position == AFTER_KEY:
            return binascii.a2b_base64(bytes(key, 'ascii'))
        else:
            raise RSAError(
                'Invalid key file %s, "%s" expected but not found' % (
                    filename,
                    START_LINE if position == BEFORE_KEY else END_LINE))


class ViriClient:
    def __init__(self, host, port, **kwargs):
        self.server = xmlrpc.client.ServerProxy('http://%s:%s/' % (host, port))

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
        description=settings.APP_DESC,
        version=settings.APP_VERSION)
    parser.add_option('--host', dest='host',
        help='destination host', default='localhost')
    parser.add_option('-p', '--port', dest='port',
        help='destination port', type='int', default=6808)
    parser.add_option('-o', '--overwrite', dest='overwrite',
        help='destination port', action='store_true', default=False)
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error('Command argument is required')
    elif args[0] not in COMMANDS.keys():
        parser.error('%s is not a %s command' % (
            args[0], settings.APP_NAME))
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

