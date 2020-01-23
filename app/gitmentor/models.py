# -*- coding: utf-8 -*-
"""Define the Grant models.

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
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel
from economy.utils import ConversionRateNotFoundError, convert_amount
from gas.utils import eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from grants.utils import get_upload_filename
from web3 import Web3


logger = logging.getLogger(__name__)


class MoneyStream(SuperModel):
    network = models.CharField(
    max_length=8,
    default='mainnet',
    help_text=_('The network in which the Sablier contract resides.'),
    )
    sablier_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('Sablier protocol contract address.'),
    )
    required_gas_price = models.DecimalField(
        default='0',
        decimal_places=0,
        max_digits=50,
        help_text=_('The required gas price for creating a Sablier stream.'),
    )
    token_address = models.CharField(max_length=50)


class SessionScheduling(SuperModel):

    """
    session_date = models.DateField(help_text=_('Requested session date.'))
    session_time = models.TimeField(help_text=_('Requested session time.'))
    # value_in_token = models.DecimalField(default=1, decimal_places=18, max_digits=50)
    # token_name = models.CharField(max_length=50)
    notes = models.TextField(help_text=_('Anything the user wants to send to the mentor.'))

    def __str__(self):
        \"""Return the string representation of a Milestone.\"""
        return (
            f"id: {self.pk}, mentor: {self.mentor}, session_type: {self.session_type}, "
            f"session_date: {self.session_date}, session_time: {self.session_time}, "
            f"notes: {notes}"
        )
    """
    SESSION_TYPE = [
        ('Debugging', 'debugging'),
        ('Code Review', 'code-review'),
        ('Peer Programming', 'peer-programming'),
        ('Other', 'other'),
    ]

    mentor = models.ManyToManyField(
        'dashboard.Profile',
        help_text=_('Select mentor'),
    )
    session_type = models.CharField(max_length=50, choices=SESSION_TYPE, blank=True, db_index=True)
    session_datetime = models.DateTimeField(help_text=_('Requested session date and time.'))

    def __str__(self):
        """Return the string representation of a Milestone."""
        return (
            f"mentor: {self.mentor}, session_type: {self.session_type}, "
            f"id: {self.pk}, session_datetime: {self.session_datetime}"
        )

class MentoringSession(SuperModel):
    pass
