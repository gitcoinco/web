class GrantCLRCalculation(SuperModel):

    latest = models.BooleanField(default=False, db_index=True, help_text="Is this calc the latest?")
    grant = models.ForeignKey(Grant, on_delete=models.CASCADE, related_name='clr_calculations',
                              help_text=_('The grant'))
    grantclr = models.ForeignKey(GrantCLR, on_delete=models.CASCADE, related_name='clr_calculations',
                              help_text=_('The grant CLR Round'))

    clr_prediction_curve = ArrayField(
        ArrayField(
            models.FloatField(),
            size=2,
        ), blank=True, default=list, help_text=_('5 point curve to predict CLR donations.'))

    def __str__(self):
        return f'{self.created_on} for g:{self.grant.pk} / gclr:{self.grantclr.pk} : {self.clr_prediction_curve}'
