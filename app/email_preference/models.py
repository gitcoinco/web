from django.contrib.postgres.fields import JSONField
from django.db import models

from economy.models import SuperModel


class EmailPreferenceLog(SuperModel):
    user_id = models.CharField(blank=True, null=True, max_length=25)
    destination = models.CharField(max_length=255, default='hubspot')
    event_data = JSONField(null=True, default=dict, blank=True)
    response_data = JSONField(null=True, default=dict, blank=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"[{self.user_id}] {self.processed_at}"
