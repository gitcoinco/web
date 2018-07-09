# -*- coding: utf-8 -*-
"""Define the Account models.

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

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse

from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel


class Organization(SuperModel):
    """Define the structure of an Organization."""

    avatar = models.ForeignKey('avatar.Avatar', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    followers = models.ManyToManyField('dashboard.Profile', related_name='follows_org')
    gh_repos_data = JSONField(default={})
    gh_user_data = JSONField(default={})
    members = models.ManyToManyField('dashboard.Profile', related_name='organizations')
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', blank=True)

    def __str__(self):
        """Return the string representation of an Organization."""
        return self.name

    def get_absolute_url(self):
        return reverse('account_organization_detail', args=(self.slug, ))

    def get_update_url(self):
        return reverse('account_organization_update', args=(self.slug, ))
