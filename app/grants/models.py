# -*- coding: utf-8 -*-
"""Define the Grant models.

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
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel
from grants.utils import get_upload_filename


class Grant(SuperModel):
    """Define the structure of a Grant."""

    status = models.BooleanField(default=True)
    title = models.CharField(default='', max_length=255)
    description = models.TextField(default='', blank=True)
    reference_url = models.URLField(db_index=True)
    image_url = models.URLField(default='')
    logo = models.ImageField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The Grant logo image.'),
    )
    logo_svg = models.FileField(
        upload_to=get_upload_filename, null=True, blank=True, help_text=_('The Grant logo SVG.')
    )
    admin_address = models.CharField(max_length=255, default='0x0')
    frequency = models.DecimalField(default=30, decimal_places=0, max_digits=50)
    amount_goal = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    amount_received = models.DecimalField(default=0, decimal_places=4, max_digits=50)
    token_address = models.CharField(max_length=255, default='0x0')
    contract_address = models.CharField(max_length=255, default='0x0')
    transaction_hash = models.CharField(max_length=255, default='0x0')
    network = models.CharField(max_length=8, default='mainnet')
    required_gas_price = models.DecimalField(default='0', decimal_places=0, max_digits=50)
    admin_profile = models.ForeignKey(
        'dashboard.Profile', related_name='grant_admin', on_delete=models.CASCADE, null=True
    )
    team_member_profiles = models.ManyToManyField('dashboard.Profile', related_name='grant_team_members')

    def percentage_done(self):
        return ((self.amount_received / self.amount_goal) * 100)

    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, status: {self.status}, title: {self.title}, description: {self.description}"


class Subscription(SuperModel):
    """Define the structure of a subscription agreement."""

    status = models.BooleanField(default=True)
    subscription_hash = models.CharField(default='', max_length=255)
    contributor_signature = models.CharField(default='', max_length=255)
    contributor_address = models.CharField(default='', max_length=255)
    amount_per_period = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    period_seconds = models.DecimalField(default=2592000, decimal_places=0, max_digits=50)
    token_address = models.CharField(max_length=255, default='0x0')
    gas_price = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    block_number = models.CharField(max_length=9, default=0)
    network = models.CharField(max_length=8, default='mainnet')
    grant = models.ForeignKey('grants.Grant', related_name='subscriptions', on_delete=models.CASCADE, null=True)
    contributor_profile = models.ForeignKey(
        'dashboard.Profile', related_name='grant_contributor', on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        """Return the string representation of a Subscription."""
        return f"id: {self.pk}, status: {self.status}, subscription_hash: {self.subscription_hash}"


class Contribution(SuperModel):
    """Define the structure of a subscription agreement."""

    tx_id = models.CharField(max_length=255, default='0x0')
    subscription = models.ForeignKey(
        'grants.Subscription', related_name='subscription_contribution', on_delete=models.CASCADE, null=True
    )
