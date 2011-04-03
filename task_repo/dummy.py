"""Creates the file /tmp/viri.output
"""

class ViriTask:
    def run(self):
        import datetime
        now = datetime.datetime.now()
        with open('/tmp/viri.output', 'w') as f:
            f.write(str(now))
            f.write(self.data_dir)
        return 'Host time: %s, Data dir: %s' % (now, self.data_dir)

