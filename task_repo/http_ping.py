"""Sends an empty get request to localhost:8080/
"""

class ViriTask:
    def run(self):
        import urllib
        urllib.urlopen('http://localhost:8000')

