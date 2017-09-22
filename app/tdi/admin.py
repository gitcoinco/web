# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import AccessCodes, WhitepaperAccess, WhitepaperAccessRequest
from django.contrib import admin


# Register your models here.
class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']


admin.site.register(WhitepaperAccessRequest, GeneralAdmin)
admin.site.register(AccessCodes, GeneralAdmin)
admin.site.register(WhitepaperAccess, GeneralAdmin)
