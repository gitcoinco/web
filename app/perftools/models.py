from django.db import models
from economy.models import SuperModel
from django.contrib.postgres.fields import JSONField

# Create your models here.


class JSONStore(SuperModel):
    """Define the JSONStore data model."""

    view = models.CharField(max_length=50, default='', blank=True, db_index=True)
    key = models.CharField(max_length=50, default='', blank=True, db_index=True)
    data = JSONField(blank=True, default={})

    def __str__(self):
        """Define the string representation of GasProfile."""
        if not self:
            return "none"
        return f" {self.view} / {self.key} "
