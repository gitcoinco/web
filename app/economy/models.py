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

import json

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.fields.files import FieldFile
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.html import escape
from django.utils.timezone import localtime


class EncodeAnything(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        elif isinstance(obj, FieldFile):
            return bool(obj)
        elif isinstance(obj, SuperModel):
            return (obj.to_standard_dict())
        elif isinstance(obj, models.Model):
            return (model_to_dict(obj))
        elif isinstance(obj, QuerySet):
            if obj.count() and type(obj.first()) == str:
                return obj[::1]
            return [json.dumps(instance, cls=EncodeAnything) for instance in obj]
        elif isinstance(obj, list):
            return [json.dumps(instance, cls=EncodeAnything) for instance in obj]
        elif(callable(obj)):
            return None
        return super(EncodeAnything, self).default(obj)


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

    def save(self, update=True, *args, **kwargs):
        """Override the SuperModel save to optionally handle modified_on logic."""
        if update:
            self.modified_on = get_time()
        return super(SuperModel, self).save(*args, **kwargs)

    def to_standard_dict(self, fields=None, exclude=None, properties=None):
        """Define the standard to dict representation of the object.

        Args:
            fields (list): The list of fields to include. If not provided,
                include all fields. If not provided, all fields are included.
                Defaults to: None.
            exclude (list): The list of fields to exclude. If not provided,
                no fields are excluded. Default to: None.

        Returns:
            dict: The dictionary representation of the object.

        """
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if exclude:
            kwargs['exclude'] = exclude
        return_me = model_to_dict(self, **kwargs)
        if properties:
            keys = [k for k in dir(self) if not k.startswith('_')]
            for key in keys:
                if key in properties:
                    attr = getattr(self, key)
                    if callable(attr):
                        return_me[key] = attr()
                    else:
                        return_me[key] = attr
        return return_me


    @property
    def admin_url(self):
        url = reverse('admin:{0}_{1}_change'.format(self._meta.app_label, self._meta.model_name), args=[self.id])
        return '{0}'.format(url, escape(str(self)))

    @property
    def created_human_time(self):
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return naturaltime(self.created_on)



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
    # If this is a fixture, don't create reverse CR.
    if not kwargs.get('raw', False):
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


class Token(SuperModel):
    """Define the Token model."""

    address = models.CharField(max_length=255, db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    network = models.CharField(max_length=25, db_index=True)
    decimals = models.IntegerField(default=18)
    priority = models.IntegerField(default=1)
    metadata = JSONField(null=True, default=dict, blank=True)
    approved = models.BooleanField(default=True)

    def __str__(self):
        """Define the string representation of a conversion rate."""
        return f"{self.symbol} on {self.network}"

    @property
    def to_dict(self):
        return {'addr': self.address, 'name': self.symbol, 'decimals': self.decimals, 'priority': self.priority}

    @property
    def to_json(self):
        import json
        return json.dumps(self.to_dict)


    @property
    def email(self):
        return self.metadata.get('email', None)
