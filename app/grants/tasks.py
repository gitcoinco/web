import datetime as dt
import math
from decimal import Decimal

from django.conf import settings
from django.utils.text import slugify

import pytz
from app.services import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from dashboard.models import Profile
from grants.models import Grant, Subscription
from grants.views import record_subscription_activity_helper
from marketing.mails import new_supporter, thank_you_for_supporting
from townsquare.models import Comment

logger = get_task_logger(__name__)

redis = RedisService().redis

CLR_START_DATE = dt.datetime(2020, 9, 14, 15, 0) # TODO:SELF-SERVICE

@app.shared_task(bind=True, max_retries=1)
def update_grant_metadata(self, grant_id, retry: bool = True) -> None:
    instance = Grant.objects.get(pk=grant_id)
    instance.contribution_count = instance.get_contribution_count
    instance.contributor_count = instance.get_contributor_count()
    instance.slug = slugify(instance.title)[:49]
    round_start_date = CLR_START_DATE.replace(tzinfo=pytz.utc)
    instance.positive_round_contributor_count = instance.get_contributor_count(round_start_date, True)
    instance.negative_round_contributor_count = instance.get_contributor_count(round_start_date, False)
    instance.twitter_handle_1 = instance.twitter_handle_1.replace('@', '')
    instance.twitter_handle_2 = instance.twitter_handle_2.replace('@', '')

    instance.amount_received_in_round = 0
    instance.amount_received = 0
    instance.monthly_amount_subscribed = 0
    instance.sybil_score = 0
    for subscription in instance.subscriptions.all():
        value_usdt = subscription.get_converted_amount(False)
        for contrib in subscription.subscription_contribution.filter(success=True):
            if value_usdt:
                instance.amount_received += Decimal(value_usdt)
                if contrib.created_on > round_start_date:
                    instance.amount_received_in_round += Decimal(value_usdt)
                    instance.sybil_score += subscription.contributor_profile.sybil_score

        if subscription.num_tx_processed <= subscription.num_tx_approved and value_usdt:
            if subscription.num_tx_approved != 1:
                instance.monthly_amount_subscribed += subscription.get_converted_monthly_amount()

    from django.contrib.contenttypes.models import ContentType
    from search.models import SearchResult
    if instance.pk:
        SearchResult.objects.update_or_create(
            source_type=ContentType.objects.get(app_label='grants', model='grant'),
            source_id=instance.pk,
            defaults={
                "created_on":instance.created_on,
                "title":instance.title,
                "description":instance.description,
                "url":instance.url,
                "visible_to":None,
                'img_url': instance.logo.url if instance.logo else None,
            }
            )
    instance.amount_received_with_phantom_funds = Decimal(round(instance.get_amount_received_with_phantom_funds(), 2))
    instance.sybil_score = instance.sybil_score / instance.positive_round_contributor_count if instance.positive_round_contributor_count else -1
    max_sybil_score = 5
    if instance.sybil_score > max_sybil_score:
        instance.sybil_score = max_sybil_score
    try:
        ss = float(instance.sybil_score)
        instance.weighted_risk_score = float(ss ** 2) * float(math.sqrt(float(instance.clr_prediction_curve[0][1])))
        if ss < 0:
            instance.weighted_risk_score = 0
    except Exception as e:
        print(e)

    # save all subscription comments
    wall_of_love = {}
    forbidden_text = 'created by ingest'
    for subscription in instance.subscriptions.all():
        if subscription.comments and forbidden_text not in subscription.comments:
            key = subscription.comments
            if key not in wall_of_love.keys():
                wall_of_love[key] = 0
            wall_of_love[key] += 1
    wall_of_love = sorted(wall_of_love.items(), key=lambda x: x[1], reverse=True)
    instance.metadata['wall_of_love'] = wall_of_love

    instance.save()


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
    grant = Grant.objects.get(pk=grant_id)
    profile = Profile.objects.get(pk=profile_id)

    if 'contributor_address' in package:
        subscription = Subscription()

        if grant.negative_voting_enabled:
            #is_postive_vote = True if package.get('is_postive_vote', 1) else False
            is_postive_vote = package.get('match_direction', '+') == '+'
        else:
            is_postive_vote = True
        subscription.is_postive_vote = is_postive_vote

        fee_pct = float(package.get('gitcoin-grant-input-amount', 0))

        subscription.active = False
        subscription.contributor_address = package.get('contributor_address', '')
        subscription.amount_per_period = package.get('amount_per_period', 0)
        subscription.real_period_seconds = package.get('real_period_seconds', 2592000)
        subscription.frequency = package.get('frequency', 30)
        subscription.frequency_unit = package.get('frequency_unit', 'days')
        subscription.token_address = package.get('token_address', '')
        subscription.token_symbol = package.get('token_symbol', '')
        subscription.gas_price = (float(subscription.amount_per_period) * (fee_pct/100))
        subscription.new_approve_tx_id = package.get('sub_new_approve_tx_id', '0x0')
        subscription.split_tx_id = package.get('split_tx_id', '0x0')
        subscription.num_tx_approved = package.get('num_tx_approved', 1)
        subscription.network = package.get('network', '')
        subscription.contributor_profile = profile
        subscription.grant = grant
        subscription.comments = package.get('comment', '')
        subscription.save()
        subscription.successful_contribution(subscription.new_approve_tx_id);

        # one time payments
        activity = None
        subscription.error = True #cancel subs so it doesnt try to bill again
        subscription.subminer_comments = "skipping subminer bc this is a 1 and done subscription, and tokens were alredy sent"
        subscription.save()
        activity = record_subscription_activity_helper('new_grant_contribution', subscription, profile)

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

        # emails to grant owner
        new_supporter(grant, subscription)
        # emails to contributor
        thank_you_for_supporting(grant, subscription)

        update_grant_metadata.delay(grant_id)
