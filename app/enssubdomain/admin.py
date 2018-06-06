# -*- coding: utf-8 -*-
"""Define ENS Subdomain related django administration sections.

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

from enssubdomain.models import ENSSubdomainRegistration


class ENSSubdomainAdmin(admin.ModelAdmin):
    """Handle displaying conversion rates in the django admin."""

    raw_id_fields = ("profile", )
    ordering = ['-id']


admin.site.register(ENSSubdomainRegistration, ENSSubdomainAdmin)
