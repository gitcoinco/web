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


class ENSSubdomainRegistration(SuperModel):
    # Defines the schema for storing ENS sub-domain registration

    github_handle = models.CharField(max_length=255, blank=False, db_index=True)
    subdomain_wallet_address = models.CharField(max_length=50)
    txn_hash = models.CharField(max_length=255)
    pending = models.BooleanField()

    def __str__(self):
        return self.github_handle
