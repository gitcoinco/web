import datetime as dt
import inspect
import math
import time
from decimal import Decimal

from django.conf import settings
from django.utils.text import slugify

import pytz
from app.services import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from dashboard.models import Profile
from grants.models import Grant, Subscription
from marketing.mails import new_grant, new_grant_admin, new_supporter, thank_you_for_supporting
from marketing.models import Stat
from perftools.models import JSONStore
from townsquare.models import Comment

logger = get_task_logger(__name__)

redis = RedisService().redis

CLR_START_DATE = dt.datetime(2020, 12, 1, 15, 0) # TODO:SELF-SERVICE


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

@app.shared_task(bind=True, max_retries=1)
def update_grant_metadata(self, grant_id, retry: bool = True) -> None:

    # KO hack 12/14/2020
    # this will prevent tasks on grants that have been issued from an app server from being immediately 
    # rewritten by the celery server.  not elegant, but it works.  perhaps in the future,
    # a delay could be introduced in the call of the task, not the task itself.
    time.sleep(1)

    # setup
    print(lineno(), round(time.time(), 2))
    instance = Grant.objects.get(pk=grant_id)
    round_start_date = CLR_START_DATE.replace(tzinfo=pytz.utc)
    if instance.in_active_clrs.exists():
        gclr = instance.in_active_clrs.order_by('start_date').first()
        round_start_date = gclr.start_date

    # grant t shirt sizing
    grant_calc_buffer = max(1, math.pow(instance.contribution_count, 1/10)) # cc
    
    # contributor counts
    do_calc = (time.time() - (900)) > instance.metadata.get('last_calc_time_contributor_counts', 0)
    if do_calc:
        print("last_calc_time_contributor_counts")
        instance.contribution_count = instance.get_contribution_count
        instance.contributor_count = instance.get_contributor_count()
        instance.positive_round_contributor_count = instance.get_contributor_count(round_start_date, True)
        instance.negative_round_contributor_count = instance.get_contributor_count(round_start_date, False)
        instance.metadata['last_calc_time_contributor_counts'] = time.time()

    # cheap calcs
    print(lineno(), round(time.time(), 2))
    instance.slug = slugify(instance.title)[:49]
    instance.twitter_handle_1 = instance.twitter_handle_1.replace('@', '')
    instance.twitter_handle_2 = instance.twitter_handle_2.replace('@', '')

    # sybil amount + amount received amount
    print(lineno(), round(time.time(), 2))
    do_calc = (time.time() - (400 * grant_calc_buffer)) > instance.metadata.get('last_calc_time_sybil_and_contrib_amounts', 0)
    if do_calc:
        print("last_calc_time_sybil_and_contrib_amounts")
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
        instance.metadata['last_calc_time_sybil_and_contrib_amounts'] = time.time()

    from django.contrib.contenttypes.models import ContentType

    print(lineno(), round(time.time(), 2))
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
    print(lineno(), round(time.time(), 2))
    if instance.sybil_score > max_sybil_score:
        instance.sybil_score = max_sybil_score
    try:
        ss = float(instance.sybil_score)
        instance.weighted_risk_score = float(ss ** 2) * float(math.sqrt(float(instance.clr_prediction_curve[0][1])))
        if ss < 0:
            instance.weighted_risk_score = 0
    except Exception as e:
        print(e)

    print(lineno(), round(time.time(), 2))
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

    # save related addresses
    # related = same contirbutor, same cart
    print(lineno(), round(time.time(), 2))
    do_calc = (time.time() - (3600 * 24)) > instance.metadata.get('last_calc_time_related', 0)
    if do_calc:
        print("last_calc_time_related")
        related = {}
        from django.utils import timezone
        for subscription in instance.subscriptions.all():
            _from = subscription.created_on - timezone.timedelta(hours=1)
            _to = subscription.created_on + timezone.timedelta(hours=1)
            profile = subscription.contributor_profile
            for _subs in profile.grant_contributor.filter(created_on__gt=_from, created_on__lt=_to).exclude(grant__id=grant_id):
                key = _subs.grant.pk
                if key not in related.keys():
                    related[key] = 0
                related[key] += 1
        instance.metadata['related'] = sorted(related.items() ,  key=lambda x: x[1], reverse=True)
        instance.metadata['last_calc_time_related'] = time.time()
    print(lineno(), round(time.time(), 2))

    instance.calc_clr_round()
    print(lineno(), round(time.time(), 2))
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
    from grants.views import record_subscription_activity_helper

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
        if subscription.network == 'undefined':
            # we unfortunately cannot trust the frontend to give us a valid network name
            # so this handles that case.  more details are available at
            # https://gitcoincore.slack.com/archives/C01FQV4FX4J/p1607980714026400
            if not settings.DEBUG:
                subscription.network = 'mainnet'
        subscription.contributor_profile = profile
        subscription.grant = grant
        subscription.comments = package.get('comment', '')
        subscription.save()

        include_for_clr = package.get('include_for_clr')

        subscription.successful_contribution(
            subscription.new_approve_tx_id,
            include_for_clr,
            checkout_type=package.get('checkout_type', None)
        )

        # one time payments
        activity = None
        subscription.error = True #cancel subs so it doesnt try to bill again
        subscription.subminer_comments = "skipping subminer bc this is a 1 and done subscription, and tokens were alredy sent"
        subscription.save()


        if 'hide_wallet_address' in package:
            profile.hide_wallet_address = bool(package.get('hide_wallet_address', False))
            profile.save()

        if 'anonymize_gitcoin_grants_contributions' in package:
            profile.anonymize_gitcoin_grants_contributions = package.get('anonymize_gitcoin_grants_contributions')
            profile.save()

        activity_profile = profile if not profile.anonymize_gitcoin_grants_contributions else Profile.objects.get(handle='gitcoinbot')

        activity = record_subscription_activity_helper('new_grant_contribution', subscription, activity_profile)

        if 'comment' in package:
            _profile = profile
            comment = package.get('comment')
            if comment and activity:
                if profile.anonymize_gitcoin_grants_contributions:
                    _profile = Profile.objects.filter(handle='gitcoinbot').first()
                    comment = f"Comment from contributor: {comment}"
                comment = Comment.objects.create(
                    profile=_profile,
                    activity=activity,
                    comment=comment)

        # emails to grant owner
        new_supporter(grant, subscription)

        # emails to contributor
        thank_you_for_supporting(grant, subscription)
        update_grant_metadata.delay(grant_id)


@app.shared_task(bind=True, max_retries=1)
def recalc_clr(self, grant_id, retry: bool = True) -> None:
    obj = Grant.objects.get(pk=grant_id)
    from django.utils import timezone

    from grants.clr import predict_clr
    for clr_round in obj.in_active_clrs.all():
        network = 'mainnet'
        predict_clr(
            save_to_db=True,
            from_date=timezone.now(),
            clr_round=clr_round,
            network=network,
            only_grant_pk=obj.pk
        )


@app.shared_task(bind=True, max_retries=1)
def process_predict_clr(self, save_to_db, from_date, clr_round, network) -> None:
    from grants.clr import predict_clr

    print(f"CALCULATING CLR estimates for ROUND: {clr_round.round_num} {clr_round.sub_round_slug}")

    predict_clr(
        save_to_db,
        from_date,
        clr_round,
        network
    )

    print(f"finished CLR estimates for {clr_round.round_num} {clr_round.sub_round_slug}")

    # TOTAL GRANT
    # grants = Grant.objects.filter(network=network, hidden=False, active=True, link_to_new_grant=None)
    # grants = grants.filter(**clr_round.grant_filters)

    # total_clr_distributed = 0
    # for grant in grants:
    #     total_clr_distributed += grant.clr_prediction_curve[0][1]

    # print(f'Total CLR allocated for {clr_round.round_num} - {total_clr_distributed}')


@app.shared_task(bind=True, max_retries=3)
def process_grant_creation_email(self, grant_id, profile_id):
    grant = Grant.objects.get(pk=grant_id)
    profile = Profile.objects.get(pk=profile_id)

    new_grant(grant, profile)
