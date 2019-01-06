from django.db import models
from economy.models import SuperModel

# Create your models here.
class Event_ETHDenver2019_Customizing_Kudos(SuperModel):
    # kudos that is required
    kudos_required = models.OneToOneField(
        'kudos.Token', on_delete=models.SET_NULL, null=True, blank=True
    )
    # active?
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'event - require kudos {self.kudos_required.name} - active: {self.active}'
