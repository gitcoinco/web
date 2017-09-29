'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import AccessCodes, WhitepaperAccess, WhitepaperAccessRequest
from django.contrib import admin


# Register your models here.
class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']


class WhitepaperAccessRequestAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['pk', 'link', 'role', 'processed', 'comments', 'email', 'created_on']
    readonly_fields = ['link']

    def link(self, instance):
        if instance.processed:
            return 'n/a'
        link = "<a href=/_administration/process_accesscode_request/{}>process me</a>".format(instance.pk)
        return link
    link.allow_tags = True


admin.site.register(WhitepaperAccessRequest, WhitepaperAccessRequestAdmin)
admin.site.register(AccessCodes, GeneralAdmin)
admin.site.register(WhitepaperAccess, GeneralAdmin)
