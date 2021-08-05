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
from .donation import Donation
from .flag import Flag
from .grant_category import GrantCategory
from .grant import Grant, GrantCLR, GrantCLRCalculation, GrantType
from .subscription import Subscription
from .grant_collection import GrantCollection
from .grant_api_key import GrantAPIKey
from .grant_stat import GrantStat
from .match_pledge import MatchPledge
from .phantom_funding import PhantomFunding

logger = logging.getLogger(__name__)



def next_month():
    """Get the next month time."""
    return localtime(timezone.now() + timedelta(days=30))


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
