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
        parser.description = 'gets and returns the content of a remote file'
        parser.add_argument('path', help='path of the file to return')

    def run(self, path):
        script_id = self.send_file(__file__)

        success, result = self.connection.execute({
            'file_name_or_id': script_id,
            'args': (path,)})

        if success:
            return result
        else:
            return (1, None, result)

class Remote:
    def run(self, path):
        import os

        if os.path.isfile(path):
            with open(path, 'r') as f:
                return [True, f.read(), None]
        else:
            return [False, None, 'File not found']

ViriScript = Remote # for compatibility with old versions

