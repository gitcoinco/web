
import logging
from datetime import datetime

from django.utils import timezone

from townsquare.models import Comment

logger = logging.getLogger(__name__)


def is_txn_done_recently(time_of_txn, before_hours=500):
    if not time_of_txn:
        return False

    now = timezone.now().replace(tzinfo=None)
    txn_should_be_done_before = now - timezone.timedelta(hours=before_hours)
    time_of_txn = datetime.fromtimestamp(int(time_of_txn))

    if time_of_txn > txn_should_be_done_before:
        return True
    return False


def txn_already_used(txn, token_symbol):
    from grants.models import Contribution

    return Contribution.objects.filter(
        tx_id = txn,
        subscription__token_symbol = token_symbol,
        success=True,
        tx_cleared=True
    ).exists()


def record_contribution_activity(contribution):
    from dashboard.models import Activity
    from marketing.mails import thank_you_for_supporting

    try:
        event_name = 'new_grant_contribution'

        subscription = contribution.subscription
        grant = subscription.grant

        metadata = {
            'id': subscription.id,
            'value_in_token': str(subscription.amount_per_period),
            'value_in_usdt_now': str(round(subscription.amount_per_period_usdt,2)),
            'token_name': subscription.token_symbol,
            'title': subscription.grant.title,
            'grant_url': subscription.grant.url,
            'num_tx_approved': round(subscription.num_tx_approved),
            'category': 'grant',
        }

        kwargs = {
            'activity_type': event_name,
            'grant': grant,
            'subscription': subscription,
            'profile': subscription.contributor_profile,
            'metadata': metadata
        }

        activity = Activity.objects.create(**kwargs)
        activity.populate_grant_activity_index()

        if subscription.comments and activity:
            Comment.objects.create(
                profile=subscription.contributor_profile,
                activity=activity,
                comment= subscription.comments
            )

        # note: commenting out for optimistic UI
        # successful_contribution(grant, subscription, contribution)
        # update_grant_metadata.delay(grant.pk)
        grants_with_subscription = [{
            'grant': grant,
            'subscription': subscription
        }]
        thank_you_for_supporting(grants_with_subscription)

    except Exception as e:
        logger.error(f"error in record_contribution_activity: {e} - {contribution}")
