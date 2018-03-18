# -*- coding: utf-8 -*-
"""Define admin related functionality for faucet.

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
from django.utils.safestring import mark_safe

from .models import FaucetRequest


class GeneralAdmin(admin.ModelAdmin):
    """Define the Faucet specific admin handling."""

    ordering = ['-id']


class FaucetRequestAdmin(admin.ModelAdmin):
    """Setup the FaucetRequest admin results display."""

    ordering = ['-created_on']
    list_display = ['created_on', 'fulfilled', 'rejected', 'link', 'github_username', 'address', 'email', 'comment']

    def link(self, instance):
        """Handle faucet request specific links.

        Args:
            instance (FaucetRequest): The faucet request to build a link for.

        Returns:
            str: The HTML element for the faucet request link.

        """
        if instance.fulfilled or instance.rejected:
            return 'n/a'
        link = mark_safe(f"<a href=/_administration/process_faucet_request/{instance.pk}>process me</a>")
        return link
    link.allow_tags = True


admin.site.register(FaucetRequest, FaucetRequestAdmin)
