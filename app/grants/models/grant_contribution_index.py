from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class GrantContributionIndex(SuperModel):
    """Stores the grants and round number to shich a user contributed to.
    The purpose of this table is to allow a a fast query. This will be used from 
    the `contributor_statistics`API """

    profile = models.ForeignKey('dashboard.Profile', help_text=_('Contributor'), on_delete=models.CASCADE, db_index=True)
    grant = models.ForeignKey('Grant', help_text=_('The grant a user contributed to'), on_delete=models.CASCADE)
    round_num = models.IntegerField(help_text=_('The round number a user contributed to'))
