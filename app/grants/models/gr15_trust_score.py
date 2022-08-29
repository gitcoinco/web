from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class GR15TrustScore(SuperModel):
    """Stores the trust bonus calculations for GR15"""

    profile = models.ForeignKey(
        "dashboard.Profile",
        related_name="gr15_trustbonus",
        on_delete=models.CASCADE,
        null=False,
        unique=True,
        help_text=_("The owner of the trust bonus"),
    )

    apu_score = models.DecimalField(
        "APU Score",
        decimal_places=18,
        max_digits=64,
    )

    trust_bonus = models.DecimalField(
        "Trust bonus",
        decimal_places=2,
        max_digits=5,
    )

    last_apu_calculation = models.DateTimeField("Last APU calculation")
    last_trust_bonus_update = models.DateTimeField("Last trust bonus update")
