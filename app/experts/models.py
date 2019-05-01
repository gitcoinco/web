from django.db import models
from django.utils.translation import gettext_lazy as _

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from economy.models import SuperModel


class ExpertSession(SuperModel):
    STATUS_OPEN = 'o'
    STATUS_READY = 'r'
    STATUS_ACTIVE = 'a'
    STATUS_CLOSED = 'c'

    STATUS_CHOICES = (
        (STATUS_OPEN, 'open'),
        (STATUS_READY, 'ready'),
        (STATUS_ACTIVE, 'active'),
        (STATUS_CLOSED, 'closed')
    )

    status = models.CharField(max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_OPEN,
                              db_index=True)
    requested_by = models.ForeignKey(
        'dashboard.Profile',
        null=True,
        on_delete=models.SET_NULL,
        related_name='expert_session_requests',
    )
    title = models.CharField(max_length=255, help_text=_('The Session title.'))
    description = models.TextField(max_length=500, default='')
    # How long the requester expects the session to last, in minutes
    # expected_duration = models.IntegerField()
    # How much the requester expects to pay per x?
    # TODO should this be a string?
    # value that has accrued so far - wei value
    value = models.BigIntegerField(default=0)
    # tx in which channel was opened
    start_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    # tx hash in which expert claimed funds
    claim_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    # last signature provided by host
    signature = models.CharField(max_length=132, blank=True, null=True)
    # on-chain channel ID (sha3 of timestamp/host/guest)
    channel_id = models.CharField(max_length=132, blank=True, null=True)

    accepted_interest = models.ForeignKey(
        'experts.ExpertSessionInterest',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='expert_session_requests',
    )

    def __str__(self):
        return f'{self.requested_by}:{self.title}'

    @property
    def channel_group_name(self):
        return f'session_{self.id}'

    def send_group_message(self, action_type, data):
        """ Send a websocket message to this session's channel """
        channel_layer = get_channel_layer()
        channel_data = {
            "type": "send_group_action",
            "action_type": action_type,
            "data": data
        }
        async_to_sync(channel_layer.group_send)(self.channel_group_name, channel_data)


class ExpertSessionInterest(SuperModel):
    """ Represents interest from an Expert in joining an ExpertSession """
    session = models.ForeignKey(
        ExpertSession,
        related_name='interests',
        on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE
    )
    signature = models.CharField(max_length=132)
    main_address = models.CharField(max_length=42)
    delegate_address = models.CharField(max_length=42)

    class Meta:
        unique_together = (('session', 'profile'), )
