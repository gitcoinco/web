'''
    Copyright (C) 2017 Gitcoin Core

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

from django.db import models
from economy.models import SuperModel
from django.utils.text import slugify

class ShortCode(SuperModel):
    """Define the shortcode schema"""

    class Meta:
        """Define metadata associated with ShortCode."""

        verbose_name_plural = 'ShortCodes'
    
    num_scans = models.PositiveSmallIntegerField(default=0)
    shortcode = models.CharField(max_length=255, default='')

class Hop(SuperModel):
    """Define the hop schema"""

    class Meta:
        """Define metadata associated with Hop."""

        verbose_name_plural = 'Hops'

    twitter_username = models.CharField(max_length=255)
    twitter_profile = models.URLField()
    web3_address = models.CharField(max_length=255)
    previous_hop = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)