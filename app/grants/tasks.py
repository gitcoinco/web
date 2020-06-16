from django.conf import settings

from app.services import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from marketing.mails import thank_you_for_supporting, new_supporter
from grants.models import Subscription, Grant
from dashboard.models import Profile
from townsquare.models import Comment
from grants.views import record_subscription_activity_helper

logger = get_task_logger(__name__)

redis = RedisService().redis


@app.shared_task(bind=True, max_retries=1)
def process_grant_contribution(self, grant_id, grant_slug, profile_id, package, retry: bool = True) -> None:
    """
    :param self:
    :param grant_id:
    :param grant_slug:
    :param profile_id:
    :param package:
    :return:
    """
    grant = Grant.objects.get(pk=grant_id, slug=grant_slug)
    profile = Profile.objects.get(pk=profile_id)

    if 'contributor_address' in package:
        subscription = Subscription()

        if grant.negative_voting_enabled:
            #is_postive_vote = True if package.get('is_postive_vote', 1) else False
            is_postive_vote = package.get('match_direction', '+') == '+'
        else:
            is_postive_vote = True
        subscription.is_postive_vote = is_postive_vote

        subscription.active = False
        subscription.contributor_address = package.get('contributor_address', '')
        subscription.amount_per_period = package.get('amount_per_period', 0)
        subscription.real_period_seconds = package.get('real_period_seconds', 2592000)
        subscription.frequency = package.get('frequency', 30)
        subscription.frequency_unit = package.get('frequency_unit', 'days')
        subscription.token_address = package.get('token_address', '')
        subscription.token_symbol = package.get('token_symbol', '')
        subscription.gas_price = package.get('gas_price', 0)
        subscription.new_approve_tx_id = package.get('sub_new_approve_tx_id', '0x0')
        subscription.num_tx_approved = package.get('num_tx_approved', 1)
        subscription.network = package.get('network', '')
        subscription.contributor_profile = profile
        subscription.grant = grant
        subscription.comments = package.get('comment', '')
        subscription.save()

        # one time payments
        activity = None
        if int(subscription.num_tx_approved) == 1:
            subscription.successful_contribution(subscription.new_approve_tx_id);
            subscription.error = True #cancel subs so it doesnt try to bill again
            subscription.subminer_comments = "skipping subminer bc this is a 1 and done subscription, and tokens were alredy sent"
            subscription.save()
            activity = record_subscription_activity_helper('new_grant_contribution', subscription, profile)
        else:
            activity = record_subscription_activity_helper('new_grant_subscription', subscription, profile)

        if 'comment' in package:
            _profile = profile
            comment = package.get('comment')
            if comment and activity:
                if subscription and subscription.negative:
                    _profile = Profile.objects.filter(handle='gitcoinbot').first()
                    comment = f"Comment from contributor: {comment}"
                comment = Comment.objects.create(
                    profile=_profile,
                    activity=activity,
                    comment=comment)

        if 'hide_wallet_address' in package:
            profile.hide_wallet_address = bool(package.get('hide_wallet_address', False))
            profile.save()

        new_supporter(grant, subscription)
        thank_you_for_supporting(grant, subscription)

