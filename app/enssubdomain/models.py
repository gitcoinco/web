# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime

# Create your models here.
from economy.models import SuperModel


def get_time():
    """Get the local time."""
    return localtime(timezone.now())


class ensSubdomainReg(SuperModel):
    # Defines the schema for storing ENS sub-domain registration

    github_handle = models.CharField(max_length=255, blank=False)
    wallet_address = models.CharField(max_length=50)
    txn_hash = models.CharField()
    timestamp = models.DateTimeField(null=False, default=get_time, db_index=True)
    pending = models.BooleanField()

    def __str__(self):
        return self.github_handle
