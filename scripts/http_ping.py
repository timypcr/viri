"""Simple ping using an http POST request sending the host code, so the server
can know that both the server and virid are running
"""

class ViriScript:
    def run(self):
        import urllib.parse
        import urllib.request

        res = urllib.request.urlopen(
            urllib.parse.urljoin(
                self.conf['server_url'],
                self.conf['ping_url']),
            urllib.parse.urlencode(
                dict(host_code=self.conf['host_code'])))

        return res.read()

