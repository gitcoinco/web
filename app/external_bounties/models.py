# -*- coding: utf-8 -*-
"""Define external bounty related models.

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
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from economy.models import SuperModel
from economy.utils import convert_amount
from github.utils import org_name, repo_name


class ExternalBounty(SuperModel):
    """Define the structure of an ExternalBounty."""

    action_url = models.URLField(db_index=True, help_text="Where to send interested parties")
    active = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True, help_text="Plainext only please!")
    source_project = models.CharField(max_length=255, help_text="The upstream project being linked it..")
    amount = models.FloatField(default=1, null=True)
    amount_denomination = models.CharField(max_length=255, blank=True, help_text="ex: ETH, LTC, BTC")
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_sync_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True, default=[], help_text="comma delimited")
    github_handle = models.CharField(max_length=255, blank=True)
    payout_str = models.CharField(max_length=255, blank=True, default='', help_text="string representation of the payout (only needed it amount/denomination cannot be filled out")
    idx_fiat_price = models.DecimalField(default=0, decimal_places=4, max_digits=50)

    def __str__(self):
        """Return the string representation of an ExternalBounty."""
        return f'{self.title} {self.active} {self.created_on}'

    @property
    def url(self):
        """Return the URL associated with the external bounty."""
        return f'/universe/{self.pk}/{slugify(self.title)}'

    @property
    def github_url(self):
        """Return the Github repository URL."""
        if "https://github.com" not in self.action_url:
            raise Exception("not a github url")
        _repo_name = repo_name(self.action_url)
        _org_name = org_name(self.action_url)
        return f"https://github.com/{_org_name}/{_repo_name}"

    @property
    def github_avatar_url(self):
        """Return the local avatar URL."""
        return f"{settings.BASE_URL}funding/avatar?repo={self.github_url}&v=3"

    @property
    def avatar(self):
        """Return the github avatar or default to a specific avatar image."""
        try:
            return self.github_avatar_url
        except Exception:
            icons = [
                'paperplane.png', 'mixer2.png', 'lock.png', 'link.png', 'laptop.png', 'life_buoy.png',
                'lightbulb.png', 'pencil_ruler.png', 'pin1.png', 'pin2.png'
            ]
            i = self.pk % len(icons)
            icon = icons[i]
            return f'/static/v2/images/icons/{icon}'

    @property
    def fiat_price(self):
        """Return the fiat price."""
        if self.amount_denomination.lower() in ['usd', 'usdt']:
            return self.amount

        fiat_price = None
        try:
            fiat_price = round(convert_amount(self.amount, self.amount_denomination, 'USDT'), 2)
        except Exception:
            pass
        return fiat_price


@receiver(pre_save, sender=ExternalBounty, dispatch_uid="psave_exbounty")
def psave_exbounty(sender, instance, **kwargs):
    instance.idx_fiat_price = instance.fiat_price
    if not instance.idx_fiat_price:
        instance.idx_fiat_price = 0
