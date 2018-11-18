from django.contrib.postgres.fields import JSONField
from django.db import models

from economy.models import SuperModel

# Create your models here.


class JSONStore(SuperModel):
    """Define the JSONStore data model."""

    view = models.CharField(max_length=255, default='', blank=True, db_index=True)
    key = models.CharField(max_length=255, default='', blank=True, db_index=True)
    data = JSONField(blank=True, default=dict)

    def __str__(self):
        """Define the string representation of GasProfile."""
        if not self:
            return "none"
        return f" {self.view} / {self.key} "
