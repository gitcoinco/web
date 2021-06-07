from django.contrib.postgres.fields import JSONField
from django.db import models

from economy.models import SuperModel


class JSONStore(SuperModel):
    """Define the JSONStore data model."""

    view = models.CharField(max_length=255, default='', blank=True, db_index=True)
    key = models.CharField(max_length=255, default='', blank=True, db_index=True)
    data = JSONField(blank=True, default=dict)

    def __str__(self):
        """Define the string representation of JSONStore."""
        if not self:
            return "none"
        return f" {self.view} / {self.key} "


class StaticJsonEnv(SuperModel):
    """Define the StaticJsonEnv data model. Meant only for static env"""

    key = models.CharField(max_length=30, default='', blank=True, db_index=True)
    data = JSONField(blank=True, default=dict)

    def __str__(self):
        """Define the string representation of StaticJsonEnv."""
        if not self:
            return "none"
        return f" {self.key}"
