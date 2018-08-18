# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from economy.models import SuperModel


class Link(SuperModel):

    comments = models.TextField()
    url = models.URLField(null=True)
    shortcode = models.CharField(max_length=255, unique=True)
    uses = models.IntegerField(default=0)

    def __str__(self):
        return self.shortcode
