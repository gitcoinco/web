# class Donation(SuperModel):
#     """Define the structure of an optional donation. These donations are
#        additional funds sent to Gitcoin as part of contributing or subscribing
#        to a grant."""

#     from_address = models.CharField(
#         max_length=255,
#         default='0x0',
#         help_text=_("The sender's address."),
#     )
#     to_address = models.CharField(
#         max_length=255,
#         default='0x0',
#         help_text=_("The destination address."),
#     )
#     profile = models.ForeignKey(
#         'dashboard.Profile',
#         related_name='donations',
#         on_delete=models.SET_NULL,
#         help_text=_("The donator's profile."),
#         null=True,
#     )
#     token_address = models.CharField(
#         max_length=255,
#         default='0x0',
#         help_text=_('The token address to be used with the Grant.'),
#     )
#     token_symbol = models.CharField(
#         max_length=255,
#         default='',
#         help_text=_("The donation token's symbol."),
#     )
#     token_amount = models.DecimalField(
#         default=0,
#         decimal_places=18,
#         max_digits=64,
#         help_text=_('The donation amount in tokens.'),
#     )
#     token_amount_usdt = models.DecimalField(
#         default=0,
#         decimal_places=4,
#         max_digits=50,
#         help_text=_('The donation amount converted to USD at the moment of donation.'),
#     )
#     tx_id = models.CharField(
#         max_length=255,
#         default='0x0',
#         help_text=_('The transaction ID of the Contribution.'),
#     )
#     network = models.CharField(
#         max_length=8,
#         default='mainnet',
#         help_text=_('The network in which the Subscription resides.'),
#     )
#     donation_percentage = models.DecimalField(
#         default=0,
#         decimal_places=2,
#         max_digits=5,
#         help_text=_('The additional percentage selected when the donation is made'),
#     )
#     subscription = models.ForeignKey(
#         'grants.subscription',
#         related_name='donations',
#         on_delete=models.SET_NULL,
#         help_text=_("The recurring subscription that this donation originated from."),
#         null=True,
#     )
#     contribution = models.ForeignKey(
#         'grants.contribution',
#         related_name='donation',
#         on_delete=models.SET_NULL,
#         help_text=_("The contribution that this donation was a part of."),
#         null=True,
#     )


#     def __str__(self):
#         """Return the string representation of this object."""
#         from django.contrib.humanize.templatetags.humanize import naturaltime
#         return f"id: {self.pk}; from:{profile.handle}; {tx_id} => ${token_amount_usdt}; {naturaltime(self.created_on)}"