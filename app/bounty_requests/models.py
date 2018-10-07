# -*- coding: utf-8 -*-
"""Define bounty requests related models.

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

from django.core.validators import MinValueValidator
from django.db import models

from datetime import datetime, timedelta
import pytz

from economy.models import SuperModel

from dashboard.models import Bounty
from dashboard.utils import clean_bounty_url


class BountyQuerySet(models.QuerySet):
    """Define the Bounty Request QuerySet Manager."""
    pass


class BountyRequest(SuperModel):
    """Define the Bounty Request model."""

    STATUS_OPEN = 'o'
    STATUS_CLOSED = 'c'
    STATUS_FUNDED = 'f'

    STATUS_CHOICES = (
        (STATUS_OPEN, 'open'),
        (STATUS_CLOSED, 'closed'),
        (STATUS_FUNDED, 'funded')
    )

    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_OPEN,
                              db_index=True)
    requested_by = models.ForeignKey(
        'dashboard.Profile',
        null=True,
        on_delete=models.SET_NULL,
        related_name='bounty_requests',
    )
    github_url = models.CharField(max_length=255, default='')
    eth_address = models.CharField(max_length=50, blank=True)
    comment = models.TextField(max_length=500, default='')
    comment_admin = models.TextField(max_length=500, blank=True)
    amount = models.FloatField(blank=False, validators=[MinValueValidator(1.0)])

    objects = BountyQuerySet.as_manager()

    def __str__(self):
        """Return the string representation of BountyRequest."""
        return f"{self.requested_by.username} / {self.created_on}"

    def to_bounty(self, network=None):
        """Creates a bounty with project status as requested. """
        Bounty.objects.create(
            github_url=clean_bounty_url(self.github_url),
            idx_status='requested',
            token_name='USDT',
            value_true=float(self.amount),
            network=network,
            web3_created=datetime.now(tz=pytz.UTC),
            expires_date=datetime.now(tz=pytz.UTC) + timedelta(days=90), # Request expire in 3 months. 
            is_open=False, # By default mark this as False as this will require fund. 
            raw_data={},
            current_bounty=True # By default it would be marked as the current bounty. 
        )
