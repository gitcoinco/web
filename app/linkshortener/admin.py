# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from linkshortener.models import Link


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']

admin.site.register(Link, GeneralAdmin)
