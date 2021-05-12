# -*- coding: utf-8 -*-
"""Define faucet related models.

Copyright (C) 2021 Gitcoin Core

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

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models

from economy.models import SuperModel


class FaucetRequestManager(models.Manager):
    """Define the Faucet Request query manager."""

    def user(self, profile):
        """Fetch the FaucetRequests matching the provided profile.

        Args:
            profile (str): The Github username.

        Returns:
            QuerySet: The filtered FaucetRequest results.

        """
        return self.select_related('profile').filter(profile__username=profile)


class FaucetRequest(SuperModel):
    """Define the Faucet Request model."""

    fulfilled = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    github_username = models.CharField(max_length=255, db_index=True)
    github_meta = JSONField(default=dict, blank=True)
    address = models.CharField(max_length=50)
    email = models.CharField(max_length=255)
    comment = models.TextField(max_length=500, blank=True)
    comment_admin = models.TextField(max_length=500, blank=True)
    fulfill_date = models.DateTimeField(null=True, blank=True)
    amount = models.FloatField(default=.00025)
    profile = models.ForeignKey(
        'dashboard.Profile',
        null=True,
        on_delete=models.SET_NULL,
        related_name='faucet_requests',
    )

    objects = FaucetRequestManager()

    def __str__(self):
        """Return the string representation of FaucetRequest."""
        return f"{self.github_username} / {self.created_on}"
