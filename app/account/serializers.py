# -*- coding: utf-8 -*-
"""Define the Account API serializers.

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
from rest_framework import serializers

from . import models


class OrganizationSerializer(serializers.ModelSerializer):
    """Define the Organization API serializer."""

    class Meta:
        """Define the metadata for the Organization form."""

        model = models.Organization
        fields = (
            'slug',
            'name',
            'created_on',
            'modified_on',
            'description',
        )
