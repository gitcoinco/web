# -*- coding: utf-8 -*-
"""Define the Grant admin layout.

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
from django.contrib import admin
from django.utils.safestring import mark_safe

from grants.models import Contribution, Grant, Subscription


class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']


class GrantAdmin(GeneralAdmin):
    """Define the Grant administration layout."""

    ordering = ['-id']
    fields = [
        'title', 'description', 'reference_url', 'admin_address', 'active', 'amount_goal', 'amount_received',
        'frequency', 'token_address', 'contract_address', 'transaction_hash', 'network', 'required_gas_price',
        'logo_svg_asset', 'logo_asset', 'created_on', 'modified_on'
    ]
    readonly_fields = [
        'logo_svg_asset', 'logo_asset', 'created_on', 'modified_on', 'token_address', 'contract_address',
        'transaction_hash', 'network', 'amount_goal', 'amount_received',
    ]

    # Custom Avatars
    def logo_svg_asset(self, instance):
        """Define the logo SVG tag to be displayed in the admin."""
        if instance.logo_svg and instance.logo_svg.url:
            return mark_safe(f'<img src="{instance.svg.url}" width="300" height="300" />')
        return mark_safe('N/A')

    def logo_asset(self, instance):
        """Define the logo image tag to be displayed in the admin."""
        if instance.logo and instance.logo.url:
            return mark_safe(f'<img src="{instance.logo.url}" width="300" height="300" />')
        return mark_safe('N/A')

    logo_svg_asset.short_description = 'Logo SVG Asset'
    logo_asset.short_description = 'Logo Image Asset'


class SubscriptionAdmin(GeneralAdmin):
    """Define the Subscription administration layout."""

    pass


class ContributionAdmin(GeneralAdmin):
    """Define the Contribution administration layout."""

    pass


admin.site.register(Grant, GrantAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Contribution, ContributionAdmin)
