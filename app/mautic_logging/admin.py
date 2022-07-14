from django.contrib import admin

from .models import MauticLog


class MauticLogAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', 'endpoint', 'status_code', 'method', 'params', 'payload']
    search_fields = ['created_on', 'endpoint', 'status_code', 'method', 'params', 'payload']

admin.site.register(MauticLog, MauticLogAdmin)
