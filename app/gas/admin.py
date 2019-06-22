# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import GasAdvisory, GasGuzzler, GasProfile


class GeneralAdmin(admin.ModelAdmin):

    ordering = ['-id']
    list_display = ['created_on', '__str__']


admin.site.register(GasAdvisory, GeneralAdmin)
admin.site.register(GasGuzzler, GeneralAdmin)
admin.site.register(GasProfile, GeneralAdmin)
