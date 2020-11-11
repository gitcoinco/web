
import logging

from townsquare.models import Comment

logger = logging.getLogger(__name__)


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
    from marketing.mails import new_supporter, thank_you_for_supporting, successful_contribution
    from grants.tasks import update_grant_metadata

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
        if subscription.comments and activity:
            Comment.objects.create(
                profile=subscription.contributor_profile,
                activity=activity,
                comment= subscription.comments
            )

        # note: commenting out for optimistic UI
        # successful_contribution(grant, subscription, contribution)
        # update_grant_metadata.delay(grant.pk)
        new_supporter(grant, subscription)
        thank_you_for_supporting(grant, subscription)

    except Exception as e:
        logger.error(f"error in record_contribution_activity: {e} - {contribution}")
