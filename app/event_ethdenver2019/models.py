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


#class Event_ETHDenver2019_EthAddrToSync(SuperModel):
#    # TODO: Use either gnosis-py or some ethereum django binding
#    eth_addr = models.CharField(max_length=255, default='', blank=True)
#    sync = models.BooleanField(default=True)
#
#    def __str__(self):
#        return f'{self.eth_addr} - syncing: {self.sync}'


#class Event_ETHDenver2019_EthAddrKudosLink(SuperModel):
#    kudos = models.OneToOneField(
#        'kudos.Token', on_delete=models.SET_NULL, null=True, blank=True
#    )
#    eth_addr = models.CharField(max_length=255, default='', blank=True)
#    cloned_from_kudos = models.OneToOneField(
#        'kudos.Token', on_delete=models.SET_NULL, null=True, blank=True
#    )
#    from_sync = models.BooleanField(default=True)
#
#    def __str__(self):
#        return f'{self.eth_addr} - {self.kudos.token_id} (cloned from: {self.cloned_from_kudos.token_id}), {self.kudos.name}'
