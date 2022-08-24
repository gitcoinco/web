from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class GrantTag(SuperModel):

    name = models.CharField(
        unique=True,
        max_length=50,
        blank=False,
        null=False,
        help_text=_('Grant Tag'),
    )

    is_eligibility_tag = models.BooleanField(
        default=False,
        help_text=('Is this tag a eligibility')
    )

    def __str__(self):
        """Return the string representation of a GrantTag."""
        return f"{self.name}"
