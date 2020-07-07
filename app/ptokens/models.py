# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Gitcoin Core

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

'''
from __future__ import unicode_literals

import base64
import collections
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection, models
from django.db.models import Count, F, Q, Subquery, Sum
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from dashboard.abi import ptoken_factory_abi
from dashboard.utils import get_web3
from economy.models import SuperModel
from eth_utils import to_checksum_address

import pytz
import requests
from bleach import clean
from bounty_requests.models import BountyRequest
from bs4 import BeautifulSoup
from rest_framework import serializers
from web3 import HTTPProvider, Web3, WebsocketProvider

logger = logging.getLogger(__name__)

TX_STATUS_CHOICES = (
    ('na', 'na'),  # not applicable
    ('pending', 'pending'),
    ('success', 'success'),
    ('error', 'error'),
    ('unknown', 'unknown'),
    ('dropped', 'dropped'),
)

FACTORY_ADDRESS = '0x80D50970599E33d0D5D436A649C25b729666A015'

class PersonalTokenQuerySet(models.QuerySet):
    """Handle the manager queryset for Personal Tokens."""

    def visible(self):
        """Filter results down to visible tokens only."""
        return self.filter(hidden=False)

    def keyword(self, keyword):
        """Filter results to all Token objects containing the keywords.

        Args:
            keyword (str): The keyword to search title, issue description, and issue keywords by.

        Returns:
            kudos.models.TokenQuerySet: The QuerySet of tokens filtered by keyword.

        """
        return self.filter(
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(tags__icontains=keyword)
        )


class PersonalToken(SuperModel):
    """Define the structure of a Personal Token"""

    TOKEN_STATUS_CHOICES = [
        ('open', 'open'),
        ('progress', 'progress'),
        ('completed', 'completed'),
        ('denied', 'denied')
    ]

    token_state = models.CharField(max_length=50, choices=TOKEN_STATUS_CHOICES, default='open', db_index=True)
    network = models.CharField(max_length=255, default='', db_index=True)  # `db_index` for `/users` search
    web3_created = models.DateTimeField(db_index=True)
    token_name = models.CharField(max_length=50)
    token_symbol = models.CharField(max_length=10, null=True)
    token_address = models.CharField(max_length=50)
    token_owner_address = models.CharField(max_length=255, blank=True)
    token_owner_profile = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.SET_NULL, related_name='token_created', blank=True
    )
    total_minted = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True, help_text='Total minted')
    txid = models.CharField(max_length=255, unique=True)
    tx_status = models.CharField(max_length=9, choices=TX_STATUS_CHOICES, default='na', db_index=True)
    value = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    objects = PersonalTokenQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.token_owner_address:
            self.token_owner_address = to_checksum_address(self.token_owner_address)

        super().save(*args, **kwargs)


    @property
    def title(self):
        return self.token_symbol

    def get_holders(self):
        # Initially will be supporting DAI, so isn't necessary check the price for other tokens
        holders = []
        purchases_ptoken = PurchasePToken.objects.filter(ptoken=self)
        total_purchases = {
            purchase['token_holder_profile']: purchase['total_amount']
            for purchase in purchases_ptoken.values('token_holder_profile').annotate(total_amount=Sum('amount'))
        }

        redemptions = RedemptionToken.objects.filter(ptoken=self)
        total_redemptions = redemptions.values('redemption_requester').annotate(total_amount=Sum('total'))

        for redemption in total_redemptions:
            requester = redemption['redemption_requester']
            if redemption['total_amount'] < total_purchases[requester]:
                holders.append(requester)

        return holders

    @property
    def available_supply(self):
        # Query the contract for better results
        return self.total_minted - (self.total_purchases - self.total_redemptions)

    @property
    def total_purchases(self):
        purchases_ptoken = PurchasePToken.objects.filter(ptoken=self)
        total_purchases = purchases_ptoken.aggregate(total_amount=Sum('amount'))

        return total_purchases.get('total_amount', 0) or 0

    @property
    def total_redemptions(self):
        redemptions = RedemptionToken.objects.filter(ptoken=self)
        total_redemptions = redemptions.aggregate(total_amount=Sum('total'))
        return total_redemptions.get('total_amount', 0) or 0

    def get_hodling_amount(self, hodler):
        total = 0
        purchases_ptoken = PurchasePToken.objects.filter(ptoken=self, token_holder_profile=hodler)
        total_purchases = purchases_ptoken.aggregate(total_amount=Sum('amount'))
        redemptions = RedemptionToken.objects.filter(ptoken=self, redemption_requester=hodler).exclude(redemption_state='denied')
        total_redemptions = redemptions.aggregate(total_amount=Sum('total'))

        total += total_purchases.get('total_amount') or 0
        total -= total_redemptions.get('total_amount') or 0

        return total

    def update_tx_status(self):
        # Get transaction status
        from dashboard.utils import get_tx_status
        self.tx_status, self.tx_time = get_tx_status(self.txid, self.network, self.created_on)

        # Exit if transaction not mined, otherwise continue
        if (self.tx_status != 'success'):
            return bool(self.tx_status)

        # Get token address from event logs
        if (self.token_address == "0x0"):
            web3 = get_web3(self.network)
            receipt = web3.eth.getTransactionReceipt(self.txid)
            contract = web3.eth.contract(Web3.toChecksumAddress(FACTORY_ADDRESS), abi=ptoken_factory_abi)
            logs = contract.events.NewPToken().processReceipt(receipt)
            self.token_address = logs[0].args.token

class RedemptionToken(SuperModel):
    """Define the structure of a Redemption PToken"""

    REDEMPTION_STATUS_CHOICES = [
        ('request', 'requested'),
        ('accepted', 'accepted'),
        ('denied', 'denied'),
        ('completed', 'completed')
    ]
    ptoken = models.ForeignKey(PersonalToken, null=True, on_delete=models.SET_NULL)
    redemption_state = models.CharField(max_length=50, choices=REDEMPTION_STATUS_CHOICES, default='request', db_index=True)
    network = models.CharField(max_length=255, default='')
    reason = models.CharField(max_length=1000, blank=True)
    total = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True, help_text='Total ptokens to redeem')
    txid = models.CharField(max_length=255, blank=True)
    redemption_accepted = models.DateTimeField(null=True)
    redemption_requester = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.SET_NULL, related_name='redemptions', blank=True
    )
    tx_status = models.CharField(max_length=9, choices=TX_STATUS_CHOICES, default='na', db_index=True)
    web3_created = models.DateTimeField(null=True)

    def update_tx_status(self):
        from dashboard.utils import get_tx_status
        self.tx_status, self.tx_time = get_tx_status(self.txid, self.network, self.created_on)
        return bool(self.tx_status)


@receiver(post_save, sender=PersonalToken, dispatch_uid="PTokenActivity")
def psave_ptoken(sender, instance, **kwargs):
    pass


class PurchasePToken(SuperModel):
    ptoken = models.ForeignKey(PersonalToken, null=True, related_name='ptoken_purchases', on_delete=models.SET_NULL)
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    network = models.CharField(max_length=255)
    txid = models.CharField(max_length=255, unique=True)
    tx_status = models.CharField(max_length=9, choices=TX_STATUS_CHOICES, default='na', db_index=True)
    web3_created = models.DateTimeField(db_index=True)
    token_holder_address = models.CharField(max_length=255, blank=True)
    token_holder_profile = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.SET_NULL, related_name='ptoken_purchases', blank=True
    )

    def update_tx_status(self):
        from dashboard.utils import get_tx_status
        self.tx_status, self.tx_time = get_tx_status(self.txid, self.network, self.created_on)
        return bool(self.tx_status)
