# -*- coding: utf-8 -*-
"""Define the Gas models.

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

from django.db import models

from economy.models import SuperModel


class GasProfile(SuperModel):
    """Define the Gas Profile data model."""

    class Meta:
        """Define the metadata associated with GasProfile."""

        verbose_name_plural = 'Gas Profiles'

    gas_price = models.DecimalField(decimal_places=2, max_digits=50, db_index=True)
    mean_time_to_confirm_blocks = models.DecimalField(decimal_places=2, max_digits=50)
    mean_time_to_confirm_minutes = models.DecimalField(decimal_places=2, max_digits=50, db_index=True)
    _99confident_confirm_time_blocks = models.DecimalField(decimal_places=2, max_digits=50)
    _99confident_confirm_time_mins = models.DecimalField(decimal_places=2, max_digits=50)

    def __str__(self):
        """Define the string representation of GasProfile."""
        if not self:
            return "none"
        return f"gas_price: {self.gas_price}, mean_time_to_confirm_minutes: {self.mean_time_to_confirm_minutes} @ {self.created_on} "


class GasGuzzler(SuperModel):
    """Define the Gas Guzzler data model."""

    class Meta:
        """Define the metadata associated with GasGuzzlers."""

        verbose_name_plural = 'Gas Guzzlers'

    gas_used = models.DecimalField(decimal_places=2, max_digits=50, db_index=True)
    pct_total = models.DecimalField(decimal_places=2, max_digits=50)
    address = models.CharField(max_length=50, default='', blank=True)
    ID = models.CharField(max_length=50, default='', blank=True)

    def __str__(self):
        """Define the string representation of GasProfile."""
        return f"{self.address}/{self.pct_total}"


class GasAdvisory(SuperModel):
    """Define the Gas Advisory data model."""

    class Meta:
        """Define the metadata associated with GasAdvisory."""

        verbose_name_plural = 'Gas Advisories'

    body = models.TextField(default='', blank=True)
    active_until = models.DateTimeField()
    active = models.BooleanField(default=False)

    def __str__(self):
        """Define the string representation of GasAdvisory."""
        if not self:
            return 'none'
        return f"Gas Advisory - {'Active until ' if self.active else 'Inactive'}{self.active_until if self.active else ''}"
