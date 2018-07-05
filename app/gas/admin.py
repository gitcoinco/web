# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import GasAdvisory, GasProfile


class GeneralAdmin(admin.ModelAdmin):

    ordering = ['-id']


admin.site.register(GasAdvisory, GeneralAdmin)
admin.site.register(GasProfile, GeneralAdmin)
