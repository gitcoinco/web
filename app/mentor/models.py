# -*- coding: utf-8 -*-
"""Define models.

Copyright (C) 2020 Gitcoin Core

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
import logging
import urllib.request
from datetime import datetime
from io import BytesIO
from os import path

import pytz
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.files import File
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.utils import timezone
from django.utils.text import slugify

import environ
import pyvips
from dashboard.models import SendCryptoAsset
from economy.models import SuperModel
from eth_utils import to_checksum_address
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from pyvips.error import Error as VipsError

logger = logging.getLogger(__name__)


class MentoringAvailable(SuperModel):
    PERIOD_TIME = (
        ('5 minutes', '5 minutes'),
        ('15 minutes', '15 minutes'),
        ('30 minutes', '30 minutes'),
        ('1 hour', '1 hour'),
        ('2 hours', '2 hour'),
        ('6 hours', '6 hour'),
    )

    mentor = models.OneToOneField(
        'dashboard.Profile', related_name='mentor_availability', on_delete=models.SET_NULL, null=True
    )
    active = models.BooleanField(default=False)
    active_until = models.DateTimeField(blank=True, null=True)
    period_time = models.CharField(choices=PERIOD_TIME, default='1 hour', max_length=20)
    created_on = models.DateTimeField(auto_now=True)

    def is_active(self):
        tz = pytz.UTC
        return self.active and self.active_until.replace(tzinfo=tz) > datetime.now().replace(tzinfo=tz)

    def active_until_iso(self):
        return self.active_until.isoformat()

class Sessions(SuperModel):
    """Define the TokenRequest model."""

    TX_STATUS_CHOICES = (
        ('na', 'na'),  # not applicable
        ('pending', 'pending'),
        ('success', 'success'),
        ('error', 'error'),
        ('unknown', 'unknown'),
        ('dropped', 'dropped'),
    )

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(max_length=500, default='')
    priceFinney = models.IntegerField(default=18)

    network = models.CharField(max_length=25, db_index=True)
    to_address = models.CharField(max_length=255)
    metadata = JSONField(null=True, default=dict, blank=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    active = models.BooleanField(default=False)

    mentor_leave = models.DateTimeField(null=True, blank=True)
    mentee_leave = models.DateTimeField(null=True, blank=True)
    mentor_join = models.DateTimeField(null=True, blank=True)
    mentee_join = models.DateTimeField(null=True, blank=True)

    price_per_min = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    amount = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    tokenName = models.CharField(max_length=255, default='ETH')
    tokenAddress = models.CharField(max_length=255, blank=True)

    tx_status = models.CharField(max_length=9, choices=TX_STATUS_CHOICES, default='na', db_index=True)
    tx_id = models.CharField(max_length=255, default='', blank=True)
    tx_received_on = models.DateTimeField(null=True, blank=True)
    tx_time = models.DateTimeField(null=True, blank=True)

    mentor = models.ForeignKey(
        'dashboard.Profile', related_name='session_mentor', on_delete=models.SET_NULL, null=True
    )
    mentee = models.ForeignKey(
        'dashboard.Profile', related_name='session_mentee', on_delete=models.SET_NULL, null=True
    )
    start_datetime = models.DateTimeField(null=True)
    end_datetime = models.DateTimeField(null=True)

    def __str__(self):
        """Define the string representation of a session."""
        return f"{self.name} on {self.network} on {self.created_on}; active: {self.active} "
