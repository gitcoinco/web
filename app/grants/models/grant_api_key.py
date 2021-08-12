from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class GrantAPIKey(SuperModel):
    """Define the structure of a GrantAPIKey."""

    key = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="the api key"
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="the api secret"
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_apikey',
        on_delete=models.CASCADE,
        help_text=_('The GrantAPI key\'s profile.'),
        null=True,
    )
