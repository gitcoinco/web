from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.timezone import localtime
from django.contrib.postgres.fields import JSONField

from economy.models import SuperModel


def next_month():
    """Get the next month time."""
    return localtime(timezone.now() + timedelta(days=30))


class MatchPledge(SuperModel):
    """Define the structure of a MatchingPledge."""

    PLEDGE_TYPES = [
        ('tech', 'tech'),
        ('media', 'media'),
        ('health', 'health'),
        ('change', 'change')
    ]

    active = models.BooleanField(default=False, help_text=_('Whether or not the MatchingPledge is active.'))
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='matchPledges',
        on_delete=models.CASCADE,
        help_text=_('The MatchingPledgers profile.'),
        null=True,
    )
    amount = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The matching pledge amount in DAI.'),
    )
    pledge_type = models.CharField(max_length=15, null=True, blank=True, choices=PLEDGE_TYPES, help_text=_('CLR pledge type'))
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))
    end_date = models.DateTimeField(null=False, default=next_month)
    data = JSONField(null=True, blank=True)
    clr_round_num = models.ForeignKey(
        'grants.GrantCLR',
        on_delete=models.CASCADE,
        help_text=_('Pledge CLR Round.'),
        null=True,
        blank=True
    )

    @property
    def data_json(self):
        import json
        return json.loads(self.data)

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.profile} <> {self.amount} DAI"
