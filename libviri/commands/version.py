# Copyright 2011, Jesús Corrius <jcorrius@gmail.com>
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
        parser.description = 'returns the version of the remote server'

    def run(self):
        script_id = self.send_file(__file__)

        success, result = self.connection.execute({
            'file_name_or_id': script_id,
            'args': ()})

        if success:
            return result
        else:
            return (1, None, result)

class Remote:
    def run(self):
        from libviri import __version__
        return [True, 'virid {0}'.format(__version__), None]

ViriScript = Remote # for compatibility with old versions

