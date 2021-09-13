from django.db import models
from economy.models import SuperModel

from django.utils.translation import gettext_lazy as _



class GrantTag(SuperModel):

    name = models.CharField(
        unique=True,
        max_length=50,
        blank=False,
        null=False,
        help_text=_('Grant Tag'),
    )

    def __str__(self):
        """Return the string representation of a GrantTag."""
        return f"{self.name}"