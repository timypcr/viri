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


class Local:
    def add_arguments(self, parser):
        parser.description = 'executes a program in remote hosts'
        parser.add_argument('program', help='program name (it can be a '
            'command or executable in the remote host, or a executable in '
            'the local host, if --send argument is specified')
        parser.add_argument('argument', nargs='*',
            help='program arguments, given when executed on remote hosts')
        parser.add_argument('-s', '--send', dest='send',
            action='store_true', help='send the program file (program '
            'argument must be a local executable)')

    def run(self, program, argument, send):
        script_id = self.send_file(__file__)

        if send:
            program = self.send_file(program)
        else:
            program = program
        is_command = not send

        success, result = self.connection.execute({
            'file_name_or_id': script_id,
            'args': (program, is_command) + tuple(argument)})
        if success:
            return result
        else:
            return (1, None, result)

class ViriScript:
    def run(self, program, is_command, *args):
        import os
        import shutil
        import stat
        import tempfile
        from subprocess import Popen, PIPE

        if is_command:
            program_path = program
        else:
            filename = self.File.get_obj(self.db, program)['file_name']
            temp_dir = tempfile.mkdtemp(prefix='viri_run_')
            program_path = os.path.join(temp_dir, filename)
            self.File.save_content(self.db, program, program_path)
            if hasattr(os, 'chmod'):
                os.chmod(program_path, stat.S_IRUSR + stat.S_IXUSR)

        proc = Popen((program_path,) + args, stdout=PIPE, stderr=PIPE)
        retval = proc.wait()

        if not is_command:
            shutil.rmtree(temp_dir)

        return [retval,
            proc.stdout.read().decode('utf-8'),
            proc.stderr.read().decode('utf-8')]

