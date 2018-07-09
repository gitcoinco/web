# -*- coding: utf-8 -*-
"""Define the Account administration entries.

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
from django import forms
from django.contrib import admin

from .models import Organization


class OrganizationAdminForm(forms.ModelForm):
    """Define the Organization administration form."""

    class Meta:
        """Define the metadata for the Organization admin form."""

        model = Organization
        fields = '__all__'


class OrganizationAdmin(admin.ModelAdmin):
    """Define the Organization administration structure."""

    form = OrganizationAdminForm
    list_display = ['name', 'slug', 'created_on', 'modified_on', 'description']
    readonly_fields = [
        'name', 'slug', 'created_on', 'modified_on', 'description'
    ]


admin.site.register(Organization, OrganizationAdmin)
