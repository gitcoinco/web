from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
from economy.models import SuperModel


class DataPayload(SuperModel):
    """Define the structure of an ExternalBounty."""

    key = models.CharField(db_index=True, max_length=255, help_text=_("key for this data report"))
    report = models.CharField(max_length=255, blank=True, help_text=_("The report associated with this project"))
    payload = JSONField(default={}, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        """Return the string representation of an ExternalBounty."""
        return f'{self.key} {self.report} - {self.comments}'

    def get_payload_with_mutations(self):
        payload = self.payload
        if self.key == 'graph':
            if self.report == 'corporate america':
                for x in range(1, len(self.payload['nodes'])):
                    payload['links'].append({"source": 0, "target": x, "weight": 10})

        return payload
