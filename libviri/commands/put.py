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
        parser.description = 'copies a file to remote hosts'
        parser.add_argument('local_path', help='path of the file to send')
        parser.add_argument('remote_path', help='destination path where to '
            'copy the file in remote hosts')
        parser.add_argument('-f', '--force', dest='force',
            action='store_true', help="overwrite if file exists ")

    def run(self, local_path, remote_path, force):
        script_id = self.send_file(__file__)
        file_id = self.send_file(local_path)

        return self.connection.execute({
            'file_name_or_id': script_id,
            'args': (file_id, remote_path, force)})


class Remote:
    def save_file(self, file_id, path, force):
        import os

        if os.path.isfile(path):
            if force:
                self.File.save_content(
                    self.db,
                    file_id,
                    path)
                res = 'File overwritten'
            else:
                res = 'File already exists'
        else:
            self.File.save_content(
                self.db,
                file_id,
                path)
            res = 'File saved'

        return res

    def run(self, file_id, path, force):
        import os

        if os.path.isdir(path):
            filename = os.path.join(
                path,
                self.File.get_obj(self.db, file_id)['file_name'])
            res = self.save_file(file_id, filename, force)
        elif os.path.isdir(os.path.dirname(path)):
            res = self.save_file(file_id, path, force)
        else:
            res = 'Directory does not exist'

        return res


ViriScript = Remote # for compatibility with old versions

