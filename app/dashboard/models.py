# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models

# Create your models here.
from economy.models import SuperModel
from django.contrib.postgres.fields import JSONField
from django.contrib.humanize.templatetags.humanize import naturaltime


class Bounty(SuperModel):
    BOUNTY_TYPES = [
        ('bug', 'bug'),
        ('security', 'security'),
        ('feature', 'feature'),
        ('unknown', 'unknown'),
    ]
    EXPERIENCE_LEVELS = [
        ('beginner', 'beginner'),
        ('intermediate', 'intermediate'),
        ('advanced', 'advanced'),
        ('unknown', 'unknown'),
    ]
    PROJECT_LENGTHS = [
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('months', 'months'),
        ('unknown', 'unknown'),
    ]
    title = models.CharField(max_length=255)
    web3_created = models.DateTimeField()
    value_in_token = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    bounty_type = models.CharField(max_length=50, choices=BOUNTY_TYPES)
    project_length = models.CharField(max_length=50, choices=PROJECT_LENGTHS)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS)
    github_url = models.URLField()
    bounty_owner_address = models.CharField(max_length=50)
    bounty_owner_email = models.CharField(max_length=255, null=True)
    bounty_owner_github_username = models.CharField(max_length=255, null=True)
    claimeee_address = models.CharField(max_length=50)
    claimee_email = models.CharField(max_length=255, null=True)
    claimee_github_username = models.CharField(max_length=255, null=True)
    is_open = models.BooleanField()
    expires_date = models.DateTimeField()
    raw_data = JSONField()
    metadata = JSONField(default={})
    claimee_metadata = JSONField(default={})
    current_bounty = models.BooleanField(default=False) # whether this bounty is the most current revision one or not

    def __str__(self):
        return "{}{} {} {} {}".format( "(CURRENT) " if self.current_bounty else "" , self.title, self.value_in_token, self.token_name, self.web3_created)

class BountySyncRequest(SuperModel):
    github_url = models.URLField()
    processed = models.BooleanField()

class Subscription(SuperModel):
    email = models.EmailField(max_length=255)
    raw_data = models.TextField()
    ip = models.CharField(max_length=50)

    def __str__(self):
        return "{} {}".format(self.email, (self.created_on))
