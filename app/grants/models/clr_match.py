from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class CLRMatch(SuperModel):
    """Define the structure of a CLR Match amount."""

    round_number = models.PositiveIntegerField(blank=True, null=True)
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='clr_matches',
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The associated Grant.'),
    )
    token = models.ForeignKey(
        'economy.Token',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    amount = models.FloatField(
        help_text='Token Amount'
    )
    usd_amount = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    has_passed_kyc = models.BooleanField(default=False, help_text=_('Has this grant gone through KYC?'))
    ready_for_payout = models.BooleanField(default=False, help_text=_('Ready for regular payout or not'))
    payout_tx = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('The payout txid'),
    )
    payout_tx_date = models.DateTimeField(null=True, blank=True)
    payout_contribution = models.ForeignKey(
        'grants.Contribution',
        related_name='clr_match_payouts',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Contribution for the payout')
    )
    claim_tx = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('The claim txid'),
    )
    grant_payout = models.ForeignKey(
        'grants.GrantPayout',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='clr_matches',
        help_text=_('Grant Payout'),
    )
    merkle_claim = JSONField(
        default=dict,
        blank=True,
        help_text=_('Claim object needed to make claim against merkle contract'),
    )
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))


    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, grant: {self.grant.pk}, round: {self.round_number}, amount: {self.amount}"
