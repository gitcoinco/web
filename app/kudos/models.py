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

import logging

logger = logging.getLogger(__name__)


class MarketPlaceListing(SuperModel):
    # Kudos specific fields -- lines up with Kudos contract
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    image = models.CharField(max_length=255, null=True)
    rarity = models.IntegerField()
    price = models.IntegerField()
    num_clones_allowed = models.IntegerField(null=True, blank=True)
    num_clones_in_wild = models.IntegerField(null=True, blank=True)
    lister = models.CharField(max_length=255)  # FK to github profile
    tags = models.CharField(max_length=255, null=True)

    # Gitcoin App only fields


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
