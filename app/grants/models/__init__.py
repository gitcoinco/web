# -*- coding: utf-8 -*-
"""Define the Grant models.

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
import json
import logging
import traceback
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core import serializers
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

import pytz
import requests
from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel
from economy.utils import ConversionRateNotFoundError, convert_amount
from gas.utils import eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from grants.utils import generate_collection_thumbnail, get_upload_filename, is_grant_team_member
from townsquare.models import Comment, Favorite
from web3 import Web3

from .cart_activity import CartActivity
from .clr_match import CLRMatch
from .contribution import Contribution
from .flag import Flag
from .grant_category import GrantCategory
from .grant import Grant, GrantCLR, GrantCLRCalculation, GrantType
from .subscription import Subscription
from .grant_collection import GrantCollection
from .grant_api_key import GrantAPIKey

logger = logging.getLogger(__name__)


class Donation(SuperModel):
    """Define the structure of an optional donation. These donations are
       additional funds sent to Gitcoin as part of contributing or subscribing
       to a grant."""

    from_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_("The sender's address."),
    )
    to_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_("The destination address."),
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='donations',
        on_delete=models.SET_NULL,
        help_text=_("The donator's profile."),
        null=True,
    )
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Grant.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='',
        help_text=_("The donation token's symbol."),
    )
    token_amount = models.DecimalField(
        default=0,
        decimal_places=18,
        max_digits=64,
        help_text=_('The donation amount in tokens.'),
    )
    token_amount_usdt = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The donation amount converted to USD at the moment of donation.'),
    )
    tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction ID of the Contribution.'),
    )
    network = models.CharField(
        max_length=8,
        default='mainnet',
        help_text=_('The network in which the Subscription resides.'),
    )
    donation_percentage = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=5,
        help_text=_('The additional percentage selected when the donation is made'),
    )
    subscription = models.ForeignKey(
        'grants.subscription',
        related_name='donations',
        on_delete=models.SET_NULL,
        help_text=_("The recurring subscription that this donation originated from."),
        null=True,
    )
    contribution = models.ForeignKey(
        'grants.contribution',
        related_name='donation',
        on_delete=models.SET_NULL,
        help_text=_("The contribution that this donation was a part of."),
        null=True,
    )


    def __str__(self):
        """Return the string representation of this object."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return f"id: {self.pk}; from:{profile.handle}; {tx_id} => ${token_amount_usdt}; {naturaltime(self.created_on)}"


def next_month():
    """Get the next month time."""
    return localtime(timezone.now() + timedelta(days=30))


class MatchPledge(SuperModel):
    """Define the structure of a MatchingPledge."""

    PLEDGE_TYPES = [
        ('tech', 'tech'),
        ('media', 'media'),
        ('health', 'health'),
        ('change', 'change')
    ]

    active = models.BooleanField(default=False, help_text=_('Whether or not the MatchingPledge is active.'))
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='matchPledges',
        on_delete=models.CASCADE,
        help_text=_('The MatchingPledgers profile.'),
        null=True,
    )
    amount = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The matching pledge amount in DAI.'),
    )
    pledge_type = models.CharField(max_length=15, null=True, blank=True, choices=PLEDGE_TYPES, help_text=_('CLR pledge type'))
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))
    end_date = models.DateTimeField(null=False, default=next_month)
    data = JSONField(null=True, blank=True)
    clr_round_num = models.ForeignKey(
        'grants.GrantCLR',
        on_delete=models.CASCADE,
        help_text=_('Pledge CLR Round.'),
        null=True,
        blank=True
    )

    @property
    def data_json(self):
        import json
        return json.loads(self.data)

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.profile} <> {self.amount} DAI"


class PhantomFunding(SuperModel):
    """Define the structure of a PhantomFunding object.

    For Grants, we have a fund we’re contributing on their behalf.  just having a quick button they can push saves all the hassle of (1) asking them their wallet, (2) sending them the DAI (3) contributing it.

    """

    round_number = models.PositiveIntegerField(blank=True, null=True)
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='phantom_funding',
        on_delete=models.CASCADE,
        help_text=_('The associated grant being Phantom Funding.'),
    )

    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_phantom_funding',
        on_delete=models.CASCADE,
        help_text=_('The associated profile doing the Phantom Funding.'),
    )

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.round_number}; {self.profile} <> {self.grant}"

    def competing_phantum_funds(self):
        return PhantomFunding.objects.filter(profile=self.profile, round_number=self.round_number)

    @property
    def value(self):
        return 5/(self.competing_phantum_funds().count())

    def to_mock_contribution(self):
        context = self.to_standard_dict()
        context['subscription'] = {
            'contributor_profile': self.profile,
            'amount_per_period': self.value,
            'token_symbol': 'DAI',
        }
        context['tx_cleared'] = True
        context['success'] = True
        return context



class CollectionsQuerySet(models.QuerySet):
    """Handle the manager queryset for Collections."""

    def visible(self):
        """Filter results down to visible collections only."""
        return self.filter(hidden=False)

    def keyword(self, keyword):
        if not keyword:
            return self
        return self.filter(
            Q(description__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(profile__handle__icontains=keyword)
        )


class GrantStat(SuperModel):
    SNAPSHOT_TYPES = [
        ('total', 'total'),
        ('increment', 'increment')
    ]

    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='stats',
                              help_text=_('Grant to add stats for this grant'))
    data = JSONField(default=dict, blank=True, help_text=_('Stats for this Grant'))
    snapshot_type = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        help_text=_('Snapshot Type'),
        db_index=True,
        choices=SNAPSHOT_TYPES,
    )

    def __str__(self):
        return f'{self.snapshot_type} {self.created_on} for {self.grant.title}'


class GrantBrandingRoutingPolicy(SuperModel):
    """
    This manages the background that would be put on a grant page (or grant CLR based on a regex matching in the URL)

    For a grant, there are several models and views that handle different kinds of grants, CLRs  and categories.
    This routing policy model sits in the middle and handles the banner and background image of specific sub-url group
    """
    policy_name = models.CharField(
        max_length=25,
        help_text=_("name to make it easier to identify"),
        blank=True,
        null=True
    )
    url_pattern = models.CharField(max_length=255, help_text=_("A regex url pattern"))
    banner_image = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('The banner image for a grant page'),
    )
    priority = models.PositiveSmallIntegerField(
        help_text=_("The priority ranking of this image 1-255. Higher priorities would be loaded first")
    )
    background_image = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('Background image'),
        blank=True,
        null=True
    )
    inline_css = models.TextField(default='', blank=True, help_text=_('Inline css to customize the banner fit'))

    def __str__(self):
        return f'{self.url_pattern} >> {self.priority}'
