# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.html import format_html

from .models import AccessCodes, WhitepaperAccess, WhitepaperAccessRequest


class GeneralAdmin(admin.ModelAdmin):

    ordering = ['-id']
    list_display = ['created_on', '__str__']


class WhitepaperAccessRequestAdmin(admin.ModelAdmin):

    ordering = ['-id']
    list_display = ['pk', 'link', 'role', 'processed', 'comments', 'email', 'created_on']
    readonly_fields = ['link']

    def link(self, instance):
        if instance.processed:
            return 'n/a'
        link = format_html('<a href="/_administration/process_accesscode_request/{}">process me</a>', instance.pk)
        return link


admin.site.register(WhitepaperAccessRequest, WhitepaperAccessRequestAdmin)
admin.site.register(AccessCodes, GeneralAdmin)
admin.site.register(WhitepaperAccess, GeneralAdmin)
