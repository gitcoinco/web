
import logging

from dashboard.helpers import bounty_activity_event_adapter, get_bounty_data_for_activity
from dashboard.models import Activity, BountyEvent, BountyFulfillment

logger = logging.getLogger(__name__)


def txn_already_used(txn, token_name):
    return BountyFulfillment.objects.filter(
        payout_tx_id = txn,
        token_name=token_name,
        accepted=True
    ).exists()


def record_payout_activity(fulfillment):
    event_name = 'worker_paid'
    bounty = fulfillment.bounty
    kwargs = {
        'activity_type': event_name,
        'bounty': bounty,
        'metadata': get_bounty_data_for_activity(bounty)
    }
    kwargs['profile'] = fulfillment.funder_profile
    kwargs['metadata']['from'] = fulfillment.funder_profile.handle
    kwargs['metadata']['to'] = fulfillment.profile.handle
    kwargs['metadata']['payout_amount'] = str(fulfillment.payout_amount)
    kwargs['metadata']['token_name'] = fulfillment.token_name

    try:
        if event_name in bounty_activity_event_adapter:
            event = BountyEvent.objects.create(bounty=bounty,
                event_type=bounty_activity_event_adapter[event_name],
                created_by=kwargs['profile'])
            bounty.handle_event(event)
        Activity.objects.create(**kwargs)

    except Exception as e:
        logger.error(f"error in record_bounty_activity: {e} - {event_name} - {bounty}")
