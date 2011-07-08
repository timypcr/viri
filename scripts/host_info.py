"""Gathers some host information like OS, uptime,... and sends it to the URL
specified on the settings.
"""

class ViriScript:
    def run(self):
        import urllib.parse
        import urllib.request
        import platform

        SEP = ';'

        self.os = self._get_os()
        data = dict(
            host_code=self.conf['custom']['host_code'],
            os=SEP.join(self.os),
            patches=self._get_patches(),
            uname=SEP.join(platform.uname()),
            uptime=self._get_uptime(),
            net=self._get_net(),
            cron=self._get_cron(),
            disks=self._get_disks())

        res = urllib.request.urlopen(
            urllib.parse.urljoin(self.conf['custom']['server_url'], self.conf['custom']['host_info_url']),
            urllib.parse.urlencode(data))

        return res.read().decode('utf-8')

    def _exec_cmd(self, cmd):
        import subprocess

        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0]

    def _get_os(self):
        import platform

        VERSION_METHODS = {
            'Linux': 'dist',
            'Windows': 'win32_ver',
            'Darwin': 'mac_ver'}

        os = (platform.system(),)
        ver_attr = VERSION_METHODS.get(os[0])
        if ver_attr:
            os += getattr(platform, ver_attr)()

        return os

    def _get_patches(self):
        cmd = self.conf['custom']['patches_cmd']
        if cmd:
            return self._exec_cmd(cmd.split(' '))
        else:
            return None

    def _get_uptime(self):
        return self._exec_cmd(('uptime',))

    def _get_net(self):
        if self.os[0] == 'Linux':
            return self._exec_cmd(('/sbin/ifconfig', '-a'))
        else:
            return None

    def _get_cron(self):
        if self.os[0] == 'Linux':
            return self._exec_cmd(('crontab', '-l'))
        else:
            return None

    def _get_disks(self):
        if self.os[0] == 'Linux':
            return self._exec_cmd(('df',))
        else:
            return None

