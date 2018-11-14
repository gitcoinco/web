# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import GasAdvisory, GasGuzzler, GasHistory, GasProfile


class GeneralAdmin(admin.ModelAdmin):

    ordering = ['-id']


admin.site.register(GasHistory, GeneralAdmin)
admin.site.register(GasAdvisory, GeneralAdmin)
admin.site.register(GasGuzzler, GeneralAdmin)
admin.site.register(GasProfile, GeneralAdmin)
