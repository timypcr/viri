from django.db import models
from django.db.models.signals import post_save
from hosts.models import Host
from viri import sync_firewall_rules

class Rule(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rule_set = models.TextField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

post_save.connect(sync_firewall_rules, sender=Rule)


class HostRule(models.Model):
    host = models.ForeignKey(Host)
    rule = models.ForeignKey(Rule)
    sync = models.BooleanField(default=True)

    class Meta:
        ordering = ('host', 'rule')

    def __unicode__(self):
        return u'%s - %s' % (self.host, self.rule)

post_save.connect(sync_firewall_rules, sender=HostRule)

