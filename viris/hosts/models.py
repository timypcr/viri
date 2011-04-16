from django.db import models

class ViriServer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    private_key = models.TextField()

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class HostGroup(models.Model):
    viri_server = models.ForeignKey(ViriServer)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    

class Host(models.Model):
    host_group = models.ForeignKey(HostGroup)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ip_address = models.CharField(max_length=255)
    virid_port = models.IntegerField(blank=True, null=True)
    sync = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

