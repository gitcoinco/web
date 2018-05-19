# -*- coding: utf-8 -*-
"""Define economy related models.

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

from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime

from economy.models import SuperModel


def get_time():
    """Get the local time."""
    return localtime(timezone.now())


class ENSSubdomainRegistration(SuperModel):
    """Define the schema for storing ENS sub-domain registration info."""

    profile = models.ForeignKey('dashboard.Profile', related_name='ens_registration', null=True, on_delete=models.SET_NULL)
    subdomain_wallet_address = models.CharField(max_length=50)
    txn_hash_1 = models.CharField(max_length=255)
    txn_hash_2 = models.CharField(max_length=255)
    txn_hash_3 = models.CharField(max_length=255)
    pending = models.BooleanField()
    signed_msg = models.TextField()
    start_nonce = models.IntegerField(default=0)
    end_nonce = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.profile.handle} at {self.created_on}, {self.start_nonce} => {self.end_nonce}"
