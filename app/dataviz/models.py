from django.db import models

# Create your models here.
from economy.models import SuperModel
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _


class DataPayload(SuperModel):
    """Define the structure of an ExternalBounty."""

    key = models.CharField(db_index=True, max_length=255, help_text=_("key for this data report"))
    report = models.CharField(max_length=255, blank=True, help_text=_("The report associated with this project"))
    payload = JSONField(default=False, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        """Return the string representation of an ExternalBounty."""
        return f'{self.key} {self.report} - {self.comments}'
