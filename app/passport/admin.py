from django.contrib import admin

from .models import PassportRequest


class PassportRequestAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['profile']

admin.site.register(PassportRequest, PassportRequestAdmin)
