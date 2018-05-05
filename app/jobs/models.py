from datetime import datetime, timedelta

from django.contrib.postgres.fields import ArrayField
from django.db import models


class Jobs(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True)
    apply_location_url = models.URLField()
    apply_location_mail = models.EmailField()
    profile = models.URLField()
    active = models.BooleanField(help_text='When a job is active.')
    skills = ArrayField(models.CharField(max_length=200), blank=True, default=[])
    company = models.CharField(max_length=255)
    github_profile = models.CharField(max_length=255, default='')
    expires_date = models.DateTimeField(default=datetime.utcnow()+timedelta(days=30))

