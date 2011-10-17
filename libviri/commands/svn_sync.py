# Copyright 2011, Jesus Corrius <jcorrius@gmail.com>
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
        parser.description = 'sync svn versioned files to remote hosts'
        parser.add_argument('svn_server_path', help='svn server path of the file to sync')
        parser.add_argument('remote_path', help='destination path where to '
            'sync the file in remote hosts')
        parser.add_argument('-u', '--username', dest='username', action='store', 
            help='username to access svn repository')
        parser.add_argument('-p', '--password', dest='password', action='store',
            help='password to access svn repository')
        parser.add_argument('-sv', '--sversion', type=int, dest='sversion',
            help='Subversion version of the file in the repository')
            
    def run(self, svn_server_path, remote_path, username, password, sversion):                    
        import os, tempfile
     
        file_name = os.path.basename(svn_server_path)
        tmp_file_name = tempfile.gettempdir() + '/' + file_name
        
        if username and password:
            if sversion:
                os.system('svn export --username {0} --password {1} -r {2} {3} {4}'.format(username, password, sversion, svn_server_path, tmp_file_name))
            else:
                os.system('svn export --username {0} --password {1} {2} {3}'.format(username, password, svn_server_path, tmp_file_name))
        else:
            if sversion:
                os.system('svn export -r {0} {1} {2}'.format(sversion, svn_server_path, tmp_file_name))
            else:
                os.system('svn export {0} {1}'.format(svn_server_path, tmp_file_name))
                
        if not os.path.isfile(tmp_file_name):
            return (1, None, 'Could not get versioned file from SVN repository.\n')

        script_id = self.send_file(__file__)
        file_id = self.send_file(tmp_file_name)

        success, result = self.connection.execute({
            'file_name_or_id': script_id,
            'args': (file_id, remote_path)})
        
        if success:
            return result
        else:
            return (1, None, result)
     
class Remote:
    def get_sha1sum_filename(self, name):
        import os
        
        directory = os.path.dirname(name)
        file_name = os.path.basename(name)
        return directory + '/' + '.' + file_name + '.sha1'
        
    def save_file(self, file_id, path):
        import os
        
        self.File.save_content(self.db, file_id, path)
        sha1_filename = self.get_sha1sum_filename(path)
        with open(sha1_filename, mode='w', encoding='utf-8') as f:
            f.write(file_id)    
        return 'Remote file saved.\n'

    def run(self, file_id, path):
        import os

        if os.path.isdir(path):
            filename = os.path.join(
                path,
                self.File.get_obj(self.db, file_id)['file_name'])
               
            sha1_filename = self.get_sha1sum_filename(filename)
            if os.path.isfile(sha1_filename):
                with open(sha1_filename, encoding='utf-8') as f:
                    sha1sum = f.read().strip()
                
                with open(filename, encoding='utf8') as f:
                    data = f.read()
                    from hashlib import sha1
                    sha1file = sha1(data.encode('utf-8')).hexdigest()
                    
                if sha1file != sha1sum:
                    return [False, None, 'I refuse to update. Remote file has been modified.\n']
                
            res = [True, self.save_file(file_id, filename), None]
        else:
            res = [False, None, 'Destination directory does not exist.\n']

        return res


ViriScript = Remote # for compatibility with old versions

