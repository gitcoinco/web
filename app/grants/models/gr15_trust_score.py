from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class GR15TrustScore(SuperModel):
    """Stores the trust bonus calculations for GR15"""

    user = models.ForeignKey(
        User,
        help_text=_("User"),
        on_delete=models.CASCADE,
        db_index=True,
    )
    score = models.DecimalField(null=False, blank=False, max_digits=7, decimal_places=5)
