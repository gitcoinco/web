# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from economy.models import SuperModel


class GasProfile(SuperModel):
    gas_price = models.DecimalField(decimal_places=2, max_digits=50, db_index=True)
    mean_time_to_confirm_blocks = models.DecimalField(decimal_places=2, max_digits=50)
    mean_time_to_confirm_minutes = models.DecimalField(decimal_places=2, max_digits=50, db_index=True)
    _99confident_confirm_time_blocks = models.DecimalField(decimal_places=2, max_digits=50)
    _99confident_confirm_time_mins = models.DecimalField(decimal_places=2, max_digits=50)

    def __str__(self):
        if not self:
            return "none"
        return f"gas_price: {self.gas_price}, mean_time_to_confirm_minutes: {self.mean_time_to_confirm_minutes} "
