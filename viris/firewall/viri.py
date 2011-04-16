import os
import models

def sync_firewall_rules(instance, **kwargs):
    params = {}
    if isinstance(instance, models.Rule):
        pass
    elif isinstance(instance, models.HostRule):
        params['ip'] = instance.host.ip_address
        params['port'] = instance.host.viri_port or 6808
        params['rules'] = instance.rule.rule_set if instance.sync or ''

    cmd = 'viric %(cmd)s --host=%(ip)s --port=%(port)s %(filename)s'

    params['cmd'] = 'send_data'
    params['filename'] = 'send_data'
    os.system(cmd % params)

    params['cmd'] = 'send_exec_task'
    os.system(cmd % params)

