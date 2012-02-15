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
import imp
from hashlib import sha1
from libviri.virirpc import XMLRPCClient, Binary

DEFAULT_PORT = 6808
LOCAL_CLASS_NAME = 'Local'

class ViriError(Exception):
    pass


class BaseCommand(object):
    def add_arguments(self, parser):
        pass

    def run(self):
        pass
        
    def connect_and_run(self, host, run, hosts, keyfile, certfile, timeout, **args):        
        self.connection = XMLRPCClient(
            'https://{0}/'.format(
                host if ':' in host else ':'.join(
                    [host, str(DEFAULT_PORT)])),
            keyfile,
            certfile,
            timeout)
        result = self.run(**args)

        check_std = lambda x: isinstance(x, str) or x == None

        result_ok = False
        if len(result) == 3:
            retval, stdout, stderr = result
            if isinstance(retval, int) and \
                check_std(stdout) and check_std(stderr):
                result_ok = True

        if result_ok:
            return result
        else:
            raise ViriError('command Local class must return a tuple of '
                '(int, str, str), representing (retval, stdout, stderr)')

    def send_file(self, filename):
        with open(filename, 'rb') as f:
            content = f.read()
        file_id = sha1(content).hexdigest()
        success, exists_value = self.connection.exists({'file_id': file_id})
        if success:
            if not exists_value:
                success, put_value = self.connection.put({
                    'file_name': os.path.basename(filename),
                    'file_content': Binary(content)})
                if not success:
                    raise ViriError('Could not send file: {}'.format(
                        put_value))
        else:
            raise ViriError('Could not check if file exists: {}'.format(
                exists_value))

        return file_id

def get_command_dirs():
    dirnames = [
        os.path.expanduser(os.path.join(
            '~',
            '.viri',
            'commands')),
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'commands')]

    return dirnames

def get_command(cmd_name):
    dirnames = get_command_dirs()

    try:
        file_obj, path, desc = imp.find_module(cmd_name, dirnames)
    except ImportError:
        raise ViriError('unknown command {}'.format(cmd_name))
    else:
        mod = imp.load_module(cmd_name, file_obj, path, desc)
        if hasattr(mod, LOCAL_CLASS_NAME):
            Local = getattr(mod, LOCAL_CLASS_NAME)
            mod.Local = type(LOCAL_CLASS_NAME, (Local, BaseCommand), {})
            return mod
        else:
            raise ViriError('command {} found, but contains errors'.format(
                cmd_name))

def get_all_commands():
    dirnames = get_command_dirs()
    commands = []

    for dirname in dirnames:
        if os.path.isdir(dirname):
            for filename in os.listdir(dirname):
                basename, extension = os.path.splitext(filename)
                if basename != '__init__' and extension.startswith('.py'):
                    try:
                        command = get_command(basename)
                    except ViriError:
                        pass
                    else:
                        # Same command can be in different directories
                        if command not in commands:
                            commands.append(command)

    return commands

