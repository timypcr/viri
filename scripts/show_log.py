
class ViriScript:
    def run(self):
        with open(self.conf['logging']['log_file'], 'r') as f:
            res = f.readlines()
        return ''.join(res)

