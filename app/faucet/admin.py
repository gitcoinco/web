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
    list_display = ['created_on', '__str__']


class FaucetRequestAdmin(admin.ModelAdmin):
    """Setup the FaucetRequest admin results display."""

    raw_id_fields = ['profile']
    ordering = ['-created_on']
    list_display = [
        'created_on', 'fulfilled', 'rejected', 'link', 'get_profile_handle',
        'get_profile_email', 'email', 'address', 'comment',
    ]
    search_fields = [
        'created_on', 'fulfilled', 'rejected', 'profile__handle',
        'email', 'address', 'comment',
    ]

    def get_queryset(self, request):
        """Override the get_queryset method to include FK lookups."""
        return super(FaucetRequestAdmin, self).get_queryset(request).select_related('profile')

    def get_profile_email(self, obj):
        """Get the profile email address."""
        profile = getattr(obj, 'profile', None)
        if profile:
            return profile.email
        return 'N/A'

    get_profile_email.admin_order_field = 'email'
    get_profile_email.short_description = 'Profile Email'

    def get_profile_handle(self, obj):
        """Get the profile handle."""
        profile = getattr(obj, 'profile', None)
        if profile and profile.handle:
            return mark_safe(
                f'<a href=/_administration/dashboard/profile/{profile.pk}/change/>{profile.handle}</a>'
            )
        if obj.github_username:
            return obj.github_username
        return 'N/A'

    get_profile_handle.admin_order_field = 'handle'
    get_profile_handle.short_description = 'Profile Handle'

    def link(self, instance):
        """Handle faucet request specific links.

        Args:
            instance (FaucetRequest): The faucet request to build a link for.

        Returns:
            str: The HTML element for the faucet request link.

        """
        if instance.fulfilled or instance.rejected:
            return 'n/a'
        return mark_safe(f"<a href=/_administration/process_faucet_request/{instance.pk}>process me</a>")
    link.allow_tags = True


admin.site.register(FaucetRequest, FaucetRequestAdmin)
