# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import GasProfile


class GeneralAdmin(admin.ModelAdmin):

    ordering = ['-id']


admin.site.register(GasProfile, GeneralAdmin)
