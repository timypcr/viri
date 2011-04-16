"""Syncronize iptables rules with the Viri Server (viris)

NOTE: This is a Python 3 script
"""

class ViriTask:
    def run(self):
        import os

        FLUSH_CMD = 'iptables -F'
        RULES_FILE = 'sync_firewall_rules.iptables'

        os.system(FLUSH_CMD)
        with open(os.path.join(self.dir_data, RULES_FILE)) as f:
            for cnt, iptables_cmd in enumerate(f.readlines()):
                os.system(iptables_cmd)
                cnt += 1

        return '%s rules successfully applied' % cnt

