# -*- coding: utf-8 -*-
"""Define economy related models.

Copyright (C) 2020 Gitcoin Core

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

from django.contrib.contenttypes.models import ContentType
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

import pytz
from app.services import RedisService


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


def get_0_time():
    """Get the local time."""
    return localtime(timezone.datetime(1970, 1, 1).replace(tzinfo=pytz.utc))


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

    def to_json_dict(self, fields=None, exclude=None, properties=None):
        return json.dumps(self.to_standard_dict(fields=fields, exclude=exclude, properties=properties), cls=EncodeAnything)

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

    @property
    def content_type(self):
        ct = ContentType.objects.get_for_model(self)
        return str(ct)

    @property
    def view_count_redis_key(self):
        key = f"{self.content_type}_{self.pk}"
        return key

    def set_view_count(self, amount):
        try:
            redis = RedisService().redis
            result = redis.set(self.view_count_redis_key, amount)
        except KeyError:
            return 0

    @property
    def get_view_count(self):
        try:
            redis = RedisService().redis
            result = redis.get(self.view_count_redis_key)
            if not result:
                return 0
            return int(result.decode('utf-8'))
        except KeyError:
            return 0


class ConversionRate(SuperModel):
    """Define the conversion rate model."""
    SOURCE_TYPES = [
        ('cryptocompare', 'cryptocompare'),
        ('poloniex', 'poloniex'),
        ('uniswap', 'uniswap'),
        ('manual', 'manual'),
    ]
    from_amount = models.FloatField()
    to_amount = models.FloatField()
    timestamp = models.DateTimeField(null=False, default=get_time, db_index=True)
    source = models.CharField(max_length=30, db_index=True, choices=SOURCE_TYPES)
    from_currency = models.CharField(max_length=30, db_index=True)
    to_currency = models.CharField(max_length=30, db_index=True)

    def __str__(self):
        """Define the string representation of a conversion rate."""
        decimals = 3
        return f"{round(self.from_amount, decimals)} {self.from_currency} => {round(self.to_amount, decimals)} " \
               f"{self.to_currency} ({self.timestamp.strftime('%m/%d/%Y')} {naturaltime(self.timestamp)}, from {self.source})"


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


class TXUpdate(SuperModel):
    """Define the TXUpdate model."""

    body = JSONField(null=True, default=dict, blank=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        """Define the string representation of this object."""
        return f"{self.body['hash']}"

    def process_callbacks(self):
        tx_id = self.body['hash']
        status = self.body.get('status')
        replaceHash = self.body.get('replaceHash')
        if status:
            # https://docs.blocknative.com/webhook-api#transaction-events-state-changes
            # TODO: move processing of failed, dropped, txns from update_tx_status to here
            pass
        if replaceHash:
            # TODO: find/replace any txids that are wrong here
            # example replacement payload
            # {"r": "0x667f3b3c35715598bc244a8fef7ca432eb725806571c99c4dca00454d08ee4ce", "s": "0x67de52717d0eef915a33250c5a849458f44215e79f7df1ea0867035c0359c5e3", "v": "0x25", "to": "0x00De4B13153673BCAE2616b67bf822500d325Fc3", "gas": 21000, "from": "0x00De4B13153673BCAE2616b67bf822500d325Fc3", "hash": "0x797a61f94f7fb20528fdbedb9d28ebdedd721ad5a2b0f4d4ac991f2ca1dcfc9b", "asset": "ETH", "input": "0x", "nonce": 4154, "value": "0", "apiKey": "d1ff5891-98f0-4324-9541-e56f54252149", "status": "speedup", "system": "ethereum", "network": "main", "gasPrice": "60000000000", "blockHash": null, "monitorId": "GETH_1_C_PROD", "timeStamp": "2020-09-21T20:27:33.924Z", "blockNumber": null, "replaceHash": "0x16903550083ee036077e67539f5da0c3bea44d874845083007cdd934e152e015", "timePending": "46956", "serverVersion": "0.64.3", "monitorVersion": "0.69.1"}
            pass
        self.processed = True
        return

class Token(SuperModel):
    """Define the Token model."""

    address = models.CharField(max_length=255, db_index=True)
    symbol = models.CharField(max_length=10, db_index=True)
    network = models.CharField(max_length=25, db_index=True)
    decimals = models.IntegerField(default=18)
    priority = models.IntegerField(default=1)
    chain_id = models.IntegerField(default=1)
    network_id = models.IntegerField(default=1)
    metadata = JSONField(null=True, default=dict, blank=True)
    approved = models.BooleanField(default=True)

    def __str__(self):
        """Define the string representation of a conversion rate."""
        return f"{self.symbol} on {self.network}"

    @property
    def to_dict(self):
        return {'id': self.id, 'addr': self.address, 'name': self.symbol, 'decimals': self.decimals, 'priority': self.priority}

    @property
    def to_json(self):
        import json
        return json.dumps(self.to_dict)


    @property
    def email(self):
        return self.metadata.get('email', None)
