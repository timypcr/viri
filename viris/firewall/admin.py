from django.contrib import admin
import models

class RuleAdmin(admin.ModelAdmin):
    search_fields = ('name', 'description', 'rule_set')

class HostRuleAdmin(admin.TabularInline):
    model = models.HostRule
    extra = 0

admin.site.register(models.Rule, RuleAdmin)

