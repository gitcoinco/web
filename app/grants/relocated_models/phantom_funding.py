class PhantomFunding(SuperModel):
    """Define the structure of a PhantomFunding object.

    For Grants, we have a fund we’re contributing on their behalf.  just having a quick button they can push saves all the hassle of (1) asking them their wallet, (2) sending them the DAI (3) contributing it.

    """

    round_number = models.PositiveIntegerField(blank=True, null=True)
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='phantom_funding',
        on_delete=models.CASCADE,
        help_text=_('The associated grant being Phantom Funding.'),
    )

    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_phantom_funding',
        on_delete=models.CASCADE,
        help_text=_('The associated profile doing the Phantom Funding.'),
    )

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.round_number}; {self.profile} <> {self.grant}"

    def competing_phantum_funds(self):
        return PhantomFunding.objects.filter(profile=self.profile, round_number=self.round_number)

    @property
    def value(self):
        return 5/(self.competing_phantum_funds().count())

    def to_mock_contribution(self):
        context = self.to_standard_dict()
        context['subscription'] = {
            'contributor_profile': self.profile,
            'amount_per_period': self.value,
            'token_symbol': 'DAI',
        }
        context['tx_cleared'] = True
        context['success'] = True
        return context