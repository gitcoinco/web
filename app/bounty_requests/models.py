# -*- coding: utf-8 -*-
"""Define bounty requests related models.

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

from django.core.validators import MinValueValidator
from django.db import models

from economy.models import SuperModel


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

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        db_index=True,
        help_text='status of the bounty request'
    )

    requested_by = models.ForeignKey(
        'dashboard.Profile',
        null=True,
        on_delete=models.SET_NULL,
        related_name='bounty_requests',
        help_text='profile submitting the bounty request'
    )

    tribe = models.ForeignKey(
        'dashboard.Profile',
        null=True,
        on_delete=models.SET_NULL,
        db_index=True,
        help_text='tribe which is being requested to fund the issue'
    )

    title = models.CharField(max_length=1000, default='')
    github_url = models.CharField(max_length=255, help_text='github url of suggested bounty')
    comment = models.TextField(max_length=500, help_text='description from the requestor to justify the bounty request')
    amount = models.FloatField(blank=False, help_text='amount for which the requested bounty is to be funded', validators=[MinValueValidator(1.0)])
    token_name = models.CharField(max_length=50, default='ETH', help_text='token in which the requested bounty is to be funded')

    github_org_email = models.CharField(max_length=255, blank=True) # TODO: REMOVE
    github_org_name = models.CharField(max_length=50, blank=True) # TODO: REMOVE
    eth_address = models.CharField(max_length=50, blank=True) # TODO: REMOVE
    comment_admin = models.TextField(max_length=500, blank=True) # TODO: REMOVE

    objects = BountyQuerySet.as_manager()

    def __str__(self):
        """Return the string representation of BountyRequest."""
        return f"{self.requested_by.username if self.requested_by else 'anonymous'} / {self.created_on}"


class BountyRequestMeta(SuperModel):
    """A helper storage class for BountyRequest to keep track of dispatched emails."""

    profile = models.ForeignKey('dashboard.Profile', on_delete=models.CASCADE)
    last_feedback_sent = models.DateTimeField()
