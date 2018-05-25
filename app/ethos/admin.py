# -*- coding: utf-8 -*-
"""Define the EthOS admin layout.

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

from ethos.models import Hop, ShortCode, TwitterProfile


class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']


class TwitterProfileAdmin(GeneralAdmin):
    """Define the Twitter profile administration layout."""

    ordering = ['-id']
    fields = ['username', 'profile_picture_tag', 'created_on', 'modified_on']
    readonly_fields = ['profile_picture_tag', 'created_on', 'modified_on']

    def profile_picture_tag(self, instance):
        """Define the twitter profile picture image tag to be displayed in the admin."""
        return mark_safe(f'<img src="{instance.profile_picture.url}" width="150" height="150" />')

    profile_picture_tag.short_description = 'Twitter Profile Picture'


admin.site.register(Hop, GeneralAdmin)
admin.site.register(ShortCode, GeneralAdmin)
admin.site.register(TwitterProfile, TwitterProfileAdmin)
