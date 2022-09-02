from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class GR15TrustScore(SuperModel):
    """Stores the trust bonus calculations for GR15"""

    user = models.ForeignKey(
        User,
        related_name="gr15_trustbonus",
        on_delete=models.CASCADE,
        null=False,
        unique=True,
        help_text=_("The owner of the trust bonus"),
    )

    last_apu_score = models.DecimalField(
        "APU Score",
        decimal_places=18,
        max_digits=64,
    )

    max_apu_score = models.DecimalField(
        "Max APU Score",
        decimal_places=18,
        max_digits=64,
    )

    trust_bonus = models.DecimalField(
        "Trust bonus",
        decimal_places=2,
        max_digits=5,
    )

    last_apu_calculation_time = models.DateTimeField("Last APU calculation")
    max_apu_calculation_time = models.DateTimeField("Max APU calculation")
    trust_bonus_calculation_time = models.DateTimeField("Last trust bonus calculation", null=True, blank=True)

    stamps = JSONField("Scored stamps", default=[], null=False, blank=True)

    is_sybil = models.BooleanField("Is sybil", default=False, blank=True)
    notes = JSONField("Notes", default=[], null=True, blank=True)
