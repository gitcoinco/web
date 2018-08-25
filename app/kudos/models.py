# -*- coding: utf-8 -*-
'''
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

'''
from __future__ import unicode_literals


from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturalday
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q, Sum
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save

from economy.models import SuperModel
from dashboard.models import Profile
from dashboard.models import Tip
from eth_utils import to_checksum_address

import logging

logger = logging.getLogger(__name__)


class Email(SuperModel):

    web3_type = models.CharField(max_length=50, default='v3')
    emails = JSONField()
    url = models.CharField(max_length=255, default='', blank=True)
    tokenName = models.CharField(max_length=255)
    tokenAddress = models.CharField(max_length=255)
    amount = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    comments_priv = models.TextField(default='', blank=True)
    comments_public = models.TextField(default='', blank=True)
    ip = models.CharField(max_length=50)
    expires_date = models.DateTimeField()
    github_url = models.URLField(null=True, blank=True)
    from_name = models.CharField(max_length=255, default='', blank=True)
    from_email = models.CharField(max_length=255, default='', blank=True)
    from_username = models.CharField(max_length=255, default='', blank=True)
    username = models.CharField(max_length=255, default='')  # to username
    network = models.CharField(max_length=255, default='')
    txid = models.CharField(max_length=255, default='')
    receive_txid = models.CharField(max_length=255, default='', blank=True)
    received_on = models.DateTimeField(null=True, blank=True)
    from_address = models.CharField(max_length=255, default='', blank=True)
    receive_address = models.CharField(max_length=255, default='', blank=True)
    recipient_profile = models.ForeignKey(
        'dashboard.Profile', related_name='received_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )
    sender_profile = models.ForeignKey(
        'dashboard.Profile', related_name='sent_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )
    metadata = JSONField(default={}, blank=True)
    is_for_bounty_fulfiller = models.BooleanField(
        default=False,
        help_text='If this option is chosen, this tip will be automatically paid to the bounty'
                  ' fulfiller, not self.usernameusername.',
    )



class Token(SuperModel):
    # Kudos specific fields -- lines up with Kudos contractpass
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=510)
    image = models.CharField(max_length=255, null=True)
    rarity = models.IntegerField()
    price_finney = models.IntegerField()
    num_clones_allowed = models.IntegerField(null=True, blank=True)
    num_clones_in_wild = models.IntegerField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True)
    cloned_from_id = models.IntegerField()
    sent_from_address = models.CharField(max_length=255)

    # Extra fields added to database (not on blockchain)
    owner_address = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.owner_address = to_checksum_address(self.owner_address)
        super().save(*args, **kwargs)

    @property
    def price_in_eth(self):
        return self.price_finney / 1000

    @property
    def shortened_address(self):
        return self.owner_address[:6] + '...' + self.owner_address[38:]

    @property
    def capitalized_name(self):
        return ' '.join([x.capitalize() for x in self.name.split('_')])

    @property
    def num_clones_available(self):
        r = self.num_clones_allowed - self.num_clones_in_wild
        if r < 0:
            r = 0
        return r

    def humanize(self):
        self.owner_address = self.shortened_address
        self.name = self.capitalized_name
        self.num_clones_available = self.get_num_clones_available()
        return self


class Wallet(SuperModel):
    address = models.CharField(max_length=255, unique=True)
    profile = models.ForeignKey('dashboard.Profile', on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.address = to_checksum_address(self.address)
        super().save(*args, **kwargs)

# class KudosToken(SuperModel):

#     # Kudos specific fields -- lines up with Kudos contract
#     name = models.CharField(max_length=255)
#     description = models.CharField(max_length=255)
#     rarity = models.IntegerField()
#     price = models.IntegerField()
#     num_clones_allowed = models.IntegerField(null=True, blank=True)
#     num_clones_in_wild = models.IntegerField(null=True, blank=True)

    # Gitcoin App only fields
    # lister = models.CharField(max_length=255)

    # web3_type = models.CharField(max_length=50, default='v2')
    # from_name = models.CharField(max_length=255, default='', blank=True)
    # from_email = models.CharField(max_length=255, default='', blank=True)
    # # from_username = models.CharField(max_length=255, default='', blank=True)
    # username = models.CharField(max_length=255, default='')  # to username
    # network = models.CharField(max_length=255, default='')
    # txid = models.CharField(max_length=255, default='')
    # receive_txid = models.CharField(max_length=255, default='', blank=True)
    # received_on = models.DateTimeField(null=True, blank=True)
    # from_address = models.CharField(max_length=255, default='', blank=True)
    # receive_address = models.CharField(max_length=255, default='', blank=True)
    # # recipient_profile = models.ForeignKey(
    # #     'dashboard.Profile', related_name='received_tips', on_delete=models.SET_NULL, null=True, blank=True
    # # )
    # # sender_profile = models.ForeignKey(
    # #     'dashboard.Profile', related_name='sent_tips', on_delete=models.SET_NULL, null=True, blank=True
    # # )
    # metadata = JSONField(default={}, blank=True)

    # def __str__(self):
    #     """Return the string representation for a Kudos."""
    #     if self.web3_type == 'yge':
    #         return f"({self.network}) - {self.status}{' ORPHAN' if not self.emails else ''} " \
    #            f"{self.amount} {self.tokenName} to {self.username} from {self.from_name or 'NA'}, " \
    #            f"created: {naturalday(self.created_on)}, expires: {naturalday(self.expires_date)}"
    #     status = 'sent' if self.txid else 'not sent'
    #     status = status if not self.receive_txid else 'received'
    #     return f"{status} {self.amount} {self.tokenName} to {self.username} from {self.from_name or 'NA'}"

    # @property
    # def receive_url(self):
    #     if self.web3_type == 'yge':
    #         return self.url

    #     pk = self.metadata['priv_key']
    #     txid = self.txid
    #     network = self.network
    #     return f"{settings.BASE_URL}tip/receive/v2/{pk}/{txid}/{network}"

    # @property
    # def status(self):
    #     if self.receive_txid:
    #         return "RECEIVED"
    #     return "PENDING"

    # @property
    # def github_org_name(self):
    #     try:
    #         return org_name(self.github_url)
    #     except Exception:
    #         return None

    # def is_notification_eligible(self, var_to_check=True):
    #     """Determine whether or not a notification is eligible for transmission outside of production.

    #     Returns:
    #         bool: Whether or not the Tip is eligible for outbound notifications.

    #     """
    #     if not var_to_check or self.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
    #         return False
    #     if self.network == 'mainnet' and (settings.DEBUG or settings.ENV != 'prod'):
    #         return False
    #     if (settings.DEBUG or settings.ENV != 'prod') and settings.GITHUB_API_USER != self.github_org_name:
    #         return False
    #     return True
