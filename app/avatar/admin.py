# -*- coding: utf-8 -*-
"""Define the Avatar admin layout.

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

from avatar.models import Avatar
from dashboard.models import Profile


class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']


class ProfileInline(admin.TabularInline):
    """Define the Profile related name inline class."""

    model = Profile
    max_num = 1
    verbose_name = 'Profile'
    verbose_name_plural = 'Profile'


class AvatarAdmin(GeneralAdmin):
    """Define the Avatar administration layout."""

    ordering = ['-id']
    fields = [
        'config', 'use_github_avatar', 'svg_asset', 'custom_png_asset', 'github_svg_asset',
        'png_asset', 'created_on', 'modified_on'
    ]
    readonly_fields = ['svg_asset', 'custom_png_asset', 'github_svg_asset', 'png_asset', 'created_on', 'modified_on']
    inlines = [ProfileInline, ]

    # Custom Avatars
    def svg_asset(self, instance):
        """Define the avatar SVG tag to be displayed in the admin."""
        if instance.svg and instance.svg.url:
            return mark_safe(f'<img src="{instance.svg.url}" width="150" height="150" />')
        return mark_safe('N/A')

    def custom_png_asset(self, instance):
        """Define the custom avatar PNG tag to be displayed in the admin."""
        if instance.custom_avatar_png and instance.custom_avatar_png.url:
            return mark_safe(f'<img src="{instance.custom_avatar_png.url}" width="150" height="150" />')
        return mark_safe('N/A')

    # Github Avatars
    def github_svg_asset(self, instance):
        """Define the Github avatar PNG tag to be displayed in the admin."""
        if instance.github_svg and instance.github_svg.url:
            return mark_safe(f'<img src="{instance.github_svg.url}" width="150" height="150" />')
        return mark_safe('N/A')

    def png_asset(self, instance):
        """Define the avatar PNG tag to be displayed in the admin."""
        if instance.png and instance.png.url:
            return mark_safe(f'<img src="{instance.png.url}" width="150" height="150" />')
        return mark_safe('N/A')

    svg_asset.short_description = 'Custom SVG Asset'
    custom_png_asset.short_description = 'Custom PNG Asset'
    github_svg_asset.short_description = 'Github SVG Asset'
    png_asset.short_description = 'Github PNG Asset'


admin.site.register(Avatar, AvatarAdmin)
