# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import localtime
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime


def get_time():
    return localtime(timezone.now())


class SuperModel(models.Model):
    created_on = models.DateTimeField(null=False, default=get_time, db_index=True)
    modified_on = models.DateTimeField(null=False, default=get_time)

    def save(self, *args, **kwargs):
        self.modified_on = get_time()
        return super(SuperModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class ConversionRate(SuperModel):
    from_amount = models.FloatField()
    to_amount = models.FloatField()
    timestamp = models.DateTimeField(null=False, default=get_time, db_index=True)
    source = models.CharField(max_length=30, db_index=True)
    from_currency = models.CharField(max_length=30, db_index=True)
    to_currency = models.CharField(max_length=30, db_index=True)

    def __str__(self):
        return "{} {} => {} {} ({}, {}) {}".format(self.from_amount, self.from_currency, self.to_amount, self.to_currency, self.timestamp, self.source, naturaltime(self.created_on))


# method for updating
@receiver(post_save, sender=ConversionRate, dispatch_uid="ReverseConversionRate")
def reverse_conversion_rate(sender, instance, **kwargs):

    # to_user transaction
    ConversionRate.objects.get_or_create(
        from_amount=instance.to_amount,
        to_amount=instance.from_amount,
        timestamp=instance.timestamp,
        source=instance.source,
        from_currency=instance.to_currency,
        to_currency=instance.from_currency
        )

