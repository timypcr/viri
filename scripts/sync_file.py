"""Synchronizes a file, and optionally runs a command, in case it is a
configuration file and a service needs to be restarted or reloaded.
"""

class ViriScript:
    def run(self, file_path, file_name, reload_cmd=None, verify_cmd=None):
        old_file_name = self._fs2db(file_path)
        self._db2fs(file_name, file_path)

        res = ''
        for cmd in (verify_cmd, reload_cmd):
            if cmd:
                try:
                    res = self._exec_cmd(cmd)
                except:
                    self._db2fs(old_file_name, file_path)
                    raise

        if res:
            res = '\nReload command returned:\n{}'.format(res)
        return 'File successfully replaced. Old file saved as {}.{}'.format(
            old_file_name, res)

    def _fs2db(self, file_path):
        from hashlib import sha1

        with open(file_path, 'rb') as f:
            file_content = f.read()
        file_hash = sha1(file_content).hexdigest()
        self.File.create(self.db, dict(
            file_name=file_hash, content=file_content))

        return file_hash

    def _db2fs(self, file_name, file_path):
        file_content = self.File.get_content(self.db, file_name).content
        with open(file_path, 'wb') as f:
            f.write(file_content)

    def _exec_cmd(self, cmd):
        import subprocess

        proc = subprocess.Popen(cmd.split(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        retval = proc.wait()
        res = proc.stdout.read().decode('utf-8')
        res = proc.stderr.read().decode('utf-8')
        if retval == 0:
            return res
        else:
            raise OSError(res)

