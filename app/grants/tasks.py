import inspect
import math
import time
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from app.services import RedisService
from celery import app
from celery.utils.log import get_task_logger
from dashboard.models import Profile
from grants.models import Grant, GrantCLR, GrantCollection, Subscription
from grants.utils import get_clr_rounds_metadata, save_grant_to_notion
from marketing.mails import (
    new_contributions, new_grant, new_grant_admin, notion_failure_email, thank_you_for_supporting,
)
from townsquare.models import Comment
from unidecode import unidecode

logger = get_task_logger(__name__)

redis = RedisService().redis

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

@app.shared_task(bind=True, soft_time_limit=600, time_limit=660, max_retries=1)
def update_grant_metadata(self, grant_id, retry: bool = True) -> None:

    if settings.FLUSH_QUEUE:
        return

    network = 'mainnet'
    if settings.DEBUG:
        network = 'rinkeby'

    # KO hack 12/14/2020
    # this will prevent tasks on grants that have been issued from an app server from being immediately
    # rewritten by the celery server.  not elegant, but it works.  perhaps in the future,
    # a delay could be introduced in the call of the task, not the task itself.
    time.sleep(3)

    # setup
    print(lineno(), round(time.time(), 2))
    instance = Grant.objects.get(pk=grant_id)

    _, round_start_date, _, _ = get_clr_rounds_metadata()

    if instance.in_active_clrs.exists():
        gclr = instance.in_active_clrs.order_by('start_date').first()
        round_start_date = gclr.start_date

    # grant t shirt sizing
    grant_calc_buffer = max(1, math.pow(instance.contribution_count, 1/10)) # cc

    # contributor counts
    do_calc = (time.time() - (2 * grant_calc_buffer)) > instance.metadata.get('last_calc_time_contributor_counts', 0)
    if do_calc:
        print("last_calc_time_contributor_counts")
        instance.contribution_count = instance.get_contribution_count
        print(lineno(), round(time.time(), 2))
        instance.contributor_count = instance.get_contributor_count()
        print(lineno(), round(time.time(), 2))
        instance.positive_round_contributor_count = instance.get_contributor_count(round_start_date, True)
        print(lineno(), round(time.time(), 2))
        instance.negative_round_contributor_count = instance.get_contributor_count(round_start_date, False)
        print(lineno(), round(time.time(), 2))
        instance.metadata['last_calc_time_contributor_counts'] = time.time()

    # cheap calcs
    print(lineno(), round(time.time(), 2))
    instance.slug = slugify(unidecode(instance.title))[:49]
    instance.twitter_handle_1 = instance.twitter_handle_1.replace('@', '')
    instance.twitter_handle_2 = instance.twitter_handle_2.replace('@', '')

    # sybil amount + amount received amount
    print(lineno(), round(time.time(), 2))
    do_calc = (time.time() - (800 * grant_calc_buffer)) > instance.metadata.get('last_calc_time_sybil_and_contrib_amounts', 0)
    if do_calc:
        print("last_calc_time_sybil_and_contrib_amounts")
        instance.amount_received_in_round = 0
        instance.amount_received = 0
        instance.monthly_amount_subscribed = 0
        instance.sybil_score = 0
        for subscription in instance.subscriptions.filter(network=network):

            value_usdt = subscription.amount_per_period_usdt

            # recalculate usdt value
            created_recently = subscription.created_on > (timezone.now() - timezone.timedelta(days=10))
            if not value_usdt and created_recently:
                value_usdt = subscription.get_converted_amount(False)
                if value_usdt:
                    subscription.amount_per_period_usdt = value_usdt
                    subscription.save()

            # calcualte usdt value in aggregate
            for contrib in subscription.subscription_contribution.filter(success=True):
                if value_usdt:
                    instance.amount_received += Decimal(value_usdt)
                    if contrib.created_on.replace(tzinfo=None) > round_start_date.replace(tzinfo=None):
                        instance.amount_received_in_round += Decimal(value_usdt)
                        instance.sybil_score += subscription.contributor_profile.sybil_score if subscription.contributor_profile else 0

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

    instance.calc_clr_round()
    print(lineno(), round(time.time(), 2))
    instance.save()


@app.shared_task(bind=True, max_retries=1)
def process_grant_contribution(self, grant_id, grant_slug, profile_id, package, send_supporter_mail:bool = True, retry: bool = True):
    """
    :param self:
    :param grant_id:
    :param grant_slug:
    :param profile_id:
    :param package:
    :param send_supporter_mail:
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
        subscription.visitorId = package.get('visitorId', '')
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

        value_usdt = subscription.get_converted_amount(False)
        include_for_clr = package.get('include_for_clr')
        if value_usdt < 1 or subscription.contributor_profile.shadowbanned:
            include_for_clr = False

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
            if value_usdt >= 1 and comment and activity:
                if profile.anonymize_gitcoin_grants_contributions:
                    _profile = Profile.objects.filter(handle='gitcoinbot').first()
                    comment = f"Comment from contributor: {comment}"
                comment = Comment.objects.create(
                    profile=_profile,
                    activity=activity,
                    comment=comment)

        # emails to contributor
        if value_usdt >= 1 and send_supporter_mail:
            grants_with_subscription = [{
                'grant': grant,
                'subscription': subscription
            }]
            try:
                thank_you_for_supporting(grants_with_subscription)
            except Exception as e:
                logger.exception(e)

        update_grant_metadata.delay(grant_id)
        return grant, subscription


@app.shared_task(bind=True, max_retries=1)
def batch_process_grant_contributions(self, grants_with_payload, profile_id, retry: bool = True) -> None:
    """
    :param self:
    :param grants_with_payload: list of dicts with grant_id, grant_slug and payload
    :param profile_id:
    :return:
    """
    grants_with_subscription = []
    for grant_with_payload in grants_with_payload:
        grant_id = grant_with_payload["grant_id"]
        grant_slug = grant_with_payload["grant_slug"]
        payload = grant_with_payload["payload"]
        grant, subscription = process_grant_contribution(
            grant_id, grant_slug, profile_id, payload, send_supporter_mail=False, retry=retry
        )
        grants_with_subscription.append({
            "grant": grant,
            "subscription": subscription
        })
        recalc_clr_if_x_minutes_old.delay(grant_id, 10)
    try:
        thank_you_for_supporting(grants_with_subscription)
    except Exception as e:
        logger.exception(e)


@app.shared_task(bind=True, max_retries=1)
def recalc_clr_if_x_minutes_old(self, grant_id, minutes, retry: bool = True) -> None:

    if settings.FLUSH_QUEUE:
        return

    return # KO 2020/03/13 - disabling this while i investigate queue processing issues.
    # namely, this task was clogging up celery queues last night
    # plus, this task is strictly additive (ie estimate_clr runs every hour already), this task
    # only creates incremental stats update on top of that.

    with redis.lock(f"tasks:recalc_clr_if_x_minutes_old:{grant_id}", timeout=60 * 3):
        obj = Grant.objects.get(pk=grant_id)
        then = timezone.now() - timezone.timedelta(minutes=minutes)
        if obj.last_clr_calc_date < then:
            recalc_clr(grant_id)


@app.shared_task(bind=True, max_retries=1)
def recalc_clr(self, grant_id, retry: bool = True) -> None:

    if settings.FLUSH_QUEUE:
        return

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
            only_grant_pk=obj.pk,
            what='slim'
        )


@app.shared_task(bind=True, max_retries=1)
def process_predict_clr(self, save_to_db, from_date, clr_round, network, what) -> None:
    from grants.clr import predict_clr

    print(f"CALCULATING CLR estimates for ROUND: {clr_round.round_num} {clr_round.sub_round_slug}")

    predict_clr(
        save_to_db,
        from_date,
        clr_round,
        network,
        what=what,
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
    try:
        grant = Grant.objects.get(pk=grant_id)
        profile = Profile.objects.get(pk=profile_id)

        new_grant(grant, profile)
    except Exception as e:
        print(e)


@app.shared_task(bind=True, max_retries=3)
def process_grant_creation_admin_email(self, grant_id):
    try:
        grant = Grant.objects.get(pk=grant_id)

        new_grant_admin(grant)
    except Exception as e:
        print(e)


@app.shared_task(bind=True, max_retries=3)
def process_notion_db_write(self, grant_id):

    grant = Grant.objects.get(pk=grant_id)

    # attempt to save - fallback to an email
    try:
        # write to notion for sybil-hunters
        save_grant_to_notion(grant)
    except:
        try:
            # send as email if we fail to write to notion
            notion_failure_email(grant)
        except Exception as e:
            print(e)


@app.shared_task(bind=True, max_retries=3)
def save_contribution(self, contrib_id):
    from grants.models import Contribution
    contrib = Contribution.objects.get(pk=contrib_id)
    contrib.save()


@app.shared_task(bind=True, max_retries=3)
def process_new_contributions_email(self, grant_id):
    try:
        grant = Grant.objects.get(pk=grant_id)
        new_contributions(grant)
    except Exception as e:
        print(e)


@app.shared_task(bind=True, max_retries=3)
def generate_collection_cache(self, collection_id):
    try:
        collection = GrantCollection.objects.get(pk=collection_id)
        collection.generate_cache()
    except Exception as e:
        print(e)
