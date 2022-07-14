from django.contrib.postgres.fields import JSONField
from django.db import models

from economy.models import SuperModel


class MauticLog(SuperModel):
    """Define the MauticLog model. Used to store requests to the mautic_proxy for further analysis"""
    status_code = models.IntegerField()
    method = models.CharField(max_length=5)
    endpoint = models.TextField()
    payload = JSONField(null=True, default=dict, blank=True)
    params = JSONField(null=True, default=dict, blank=True)

    def __str__(self):
        return f"[{self.status_code}] {self.endpoint}"
