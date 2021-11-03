from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class GrantPayout(SuperModel):

    PAYOUT_STATUS = [
        ('pending', 'Pending'),
        ('ready', 'ready'),
        ('expired', 'expired'),
        ('clawed', 'clawed')
    ]

    grant_clrs = models.ForeignKey(
        'GrantCLR',
        on_delete=models.CASCADE,
        related_name='grant_clrs',
        help_text=_('Grant CLRs')
    )

    payout_contract = models.CharField(
        max_length=255,
        help_text=_('Payout Contract from which funds would be claimed')
    )

    name = models.CharField(
        max_length=25,
        help_text=_('Display Name for Payout')
    )

    status = models.CharField(
        max_length=20,
        choices=PAYOUT_STATUS,
        default='pending'
    )

# After round ends: 
# 
# Admin deploys contract (payout_contract)
# Admin would have to create an entry in GrantPayout and map it to CLR 
# Admin runs payout_round_noncustodial finalize to populate CLRMatch
# UI would rely on 
#   -> CLRMatch + GrantPayout table to what grants can claim
# When user claim 
#   -> we have to update CLRMatch.has_claimed


# CRON
#   -> Mgmt command to check all CLRMatch.has_claimed which is False 
#      and check if claim has been made


# HOW TO POPULATE OLD ONES
#   -> need to create new GrantPayout entries for older payouts
#   -> link the CLRMATCH to GrantPayout entry 
#   -> run the cron

# Update payout_round_noncustodial to use new values

# API
#   -> new API to show claim history 
#   -> new API to show new claims