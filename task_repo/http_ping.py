"""Simple ping using an http POST request sending the host code, so the server
can know that both the server and virid are running
"""

class ViriTask:
    def run(self):
        import urllib.parse
        import urllib.request

        res = urllib.request.urlopen(
            urllib.parse.urljoin(self.conf.serverurl, self.conf.pingurl),
            urllib.parse.urlencode(dict(host_code=self.conf.hostcode)))

        return res.read()

