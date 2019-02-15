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

    profile = models.ForeignKey(
        'dashboard.Profile', related_name='ens_registration', null=True, on_delete=models.SET_NULL
    )
    subdomain_wallet_address = models.CharField(max_length=50)
    txn_hash_1 = models.CharField(max_length=255, blank=True)
    txn_hash_2 = models.CharField(max_length=255, blank=True)
    txn_hash_3 = models.CharField(max_length=255, blank=True)
    pending = models.BooleanField()
    signed_msg = models.TextField()
    start_nonce = models.IntegerField(default=0)
    end_nonce = models.IntegerField(default=0)
    gas_cost_eth = models.FloatField(default=0.000649197)
    comments = models.TextField(blank=True)

    def __str__(self):
        """Return the string representation of an ENS subdomain registration."""
        return f"{self.profile.handle if self.profile else 'unknown'} at " \
               f"{self.created_on}, {self.start_nonce} => {self.end_nonce}"

    def reprocess(self, gas_multiplier=1.101, override_nonce=None):
        """Reprocess the registration request."""
        from enssubdomain.views import helper_process_registration

        self.start_nonce = 0
        self.end_nonce = 0
        self.pending = False

        signer = self.subdomain_wallet_address
        github_handle = self.profile.handle
        signed_msg = self.signed_msg
        replacement = helper_process_registration(
            signer, github_handle, signed_msg, gas_multiplier=gas_multiplier, override_nonce=override_nonce
        )
        self.comments += f"replaced by {replacement.pk}"
