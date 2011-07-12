"""Synchronizes a file, and optionally runs a command, in case it is a
configuration file and a service needs to be restarted or reloaded.
"""

class ViriScript:
    def run(self, file_path, file_name, reload_cmd=None, verify_cmd=None):
        with open(file_path, 'rb') as f:
            file_content = f.read()
        old_file_id = self.File.create(self.db, dict(
            file_name=file_name, content=file_content)).file_id
        self.File.save_content(self.db, file_name, file_path)

        res = ''
        for cmd in (verify_cmd, reload_cmd):
            if cmd:
                try:
                    res = self._exec_cmd(cmd)
                except:
                    self.File.save_content(self.db, old_file_id, file_path)
                    raise

        if res:
            res = '\nReload command returned:\n{}'.format(res)
        return 'File successfully replaced. Old file saved as {}.{}'.format(
            old_file_id, res)

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

