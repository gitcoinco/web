from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class CLRMatch(SuperModel):
    """Define the structure of a CLR Match amount."""

    round_number = models.PositiveIntegerField(blank=True, null=True)
    amount = models.FloatField()
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='clr_matches',
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The associated Grant.'),
    )
    has_passed_kyc = models.BooleanField(default=False, help_text=_('Has this grant gone through KYC?'))
    ready_for_test_payout = models.BooleanField(default=False, help_text=_('Ready for test payout or not'))
    test_payout_tx = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('The test payout txid'),
    )
    test_payout_tx_date = models.DateTimeField(null=True, blank=True)
    test_payout_contribution = models.ForeignKey(
        'grants.Contribution',
        related_name='test_clr_match_payouts',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Contribution for the test payout')
    )
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
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))


    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, grant: {self.grant.pk}, round: {self.round_number}, amount: {self.amount}"
