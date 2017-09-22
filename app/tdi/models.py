# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from economy.models import SuperModel


class AccessCodes(SuperModel):
    invitecode = models.CharField(max_length=30)
    maxuses = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.invitecode

    @property
    def uses(self):
        return WhitepaperAccess.objects.filter(invitecode=self.invitecode).count()


class WhitepaperAccess(SuperModel):
    invitecode = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    ip = models.CharField(max_length=30)

    def __str__(self):
        return "{} / {} / {} on {}".format(self.email, self.invitecode, self.ip, self.created_on)


class WhitepaperAccessRequest(SuperModel):
    comments = models.TextField(max_length=5000)
    email = models.CharField(max_length=30)
    role = models.CharField(max_length=255)
    ip = models.CharField(max_length=30)

    def __str__(self):
        return "{} / {} / {} on {}".format(self.email, self.role, self.ip, self.created_on)

