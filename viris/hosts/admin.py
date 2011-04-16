from django.contrib import admin
from django.utils.importlib import import_module
from django.conf import settings
import models

def _host_inlines():
    inlines = []
    if hasattr(settings, 'HOST_INLINES'):
        for inline in settings.HOST_INLINES:
            (mod, cls) = inline.rsplit('.', 1)
            inlines.append(getattr(
                __import__(mod, globals(), locals(), (cls,), -1),
                cls))
    return inlines

class ViriServerAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')

class HostGroupAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description')
    list_filter = ('viri_server',)

class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'host_group', 'sync')
    list_filter = ('host_group', 'sync')
    search_fields = ('name', 'description')
    inlines = _host_inlines()

admin.site.register(models.ViriServer, ViriServerAdmin)
admin.site.register(models.HostGroup, HostGroupAdmin)
admin.site.register(models.Host, HostAdmin)

