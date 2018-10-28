# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from linkshortener.models import Link


class LinkShortenerAdmin(admin.ModelAdmin):

    ordering = ['-id']
    list_display = ['shortcode', 'comments', 'uses']


admin.site.register(Link, LinkShortenerAdmin)
