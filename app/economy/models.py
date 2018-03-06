# -*- coding: utf-8 -*-
"""Define economy related models.

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

from __future__ import unicode_literals

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import localtime


def get_time():
    """Get the local time."""
    return localtime(timezone.now())


class SuperModel(models.Model):
    """Define the base abstract model."""

    class Meta:
        """Define the model metadata."""

        abstract = True

    created_on = models.DateTimeField(null=False, default=get_time, db_index=True)
    modified_on = models.DateTimeField(null=False, default=get_time)

    def save(self, *args, **kwargs):
        """Override the SuperModel save to handle modified_on logic."""
        self.modified_on = get_time()
        return super(SuperModel, self).save(*args, **kwargs)


class ConversionRate(SuperModel):
    """Define the conversion rate model."""

    from_amount = models.FloatField()
    to_amount = models.FloatField()
    timestamp = models.DateTimeField(null=False, default=get_time, db_index=True)
    source = models.CharField(max_length=30, db_index=True)
    from_currency = models.CharField(max_length=30, db_index=True)
    to_currency = models.CharField(max_length=30, db_index=True)

    def __str__(self):
        """Define the string representation of a conversion rate."""
        return f"{self.from_amount} {self.from_currency} => {self.to_amount} " \
               f"{self.to_currency} ({self.timestamp}, {self.source}) {naturaltime(self.created_on)}"


# method for updating
@receiver(post_save, sender=ConversionRate, dispatch_uid="ReverseConversionRate")
def reverse_conversion_rate(sender, instance, **kwargs):
    """Handle the reverse conversion rate signal during post-save."""
    # 1 / # 0.000979
    from_amount = float(instance.to_amount) / float(instance.from_amount)
    to_amount = 1

    # reverse transaction
    ConversionRate.objects.get_or_create(
        from_amount=from_amount,
        to_amount=to_amount,
        timestamp=instance.timestamp,
        source=instance.source,
        from_currency=instance.to_currency,
        to_currency=instance.from_currency
    )
