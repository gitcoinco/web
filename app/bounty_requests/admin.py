# -*- coding: utf-8 -*-
"""Define admin related functionality for Bounty Requests.

Copyright (C) 2018 Gitcoin Core

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
from __future__ import unicode_literals

from django.contrib import admin

from .models import BountyRequest, BountyRequestMeta


class BountyRequestAdmin(admin.ModelAdmin):
    """Setup the BountyRequest admin results display."""
    ordering = ['-created_on']
    list_display = [
        'created_on', 'status', 'github_url', 'amount', 'requested_by',
        'comment_admin'
    ]
    search_fields = [
        'created_on', 'status', 'github_url', 'amount', 'requested_by__handle',
        'eth_address', 'comment', 'comment_admin'
    ]
    raw_id_fields = ['requested_by']


admin.site.register(BountyRequest, BountyRequestAdmin)
admin.site.register(BountyRequestMeta)
