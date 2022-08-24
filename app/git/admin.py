# -*- coding: utf-8 -*-
"""Define the Grant admin layout.

Copyright (C) 2021 Gitcoin Core

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

"""
from django.contrib import admin

from git.models import GitCache


class GitCacheAdmin(admin.ModelAdmin):
    list_display = ['pk', 'category', 'handle']
    search_fields = [
        'id', 'handle'
    ]

admin.site.register(GitCache, GitCacheAdmin)
