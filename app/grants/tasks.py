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
from grants.clr import calculate_clr_for_donation, fetch_data, populate_data_for_clr
from grants.models import Grant, Subscription
from marketing.mails import new_grant, new_grant_admin, new_supporter, thank_you_for_supporting
from marketing.models import Stat
from perftools.models import JSONStore
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

    # save related addresses
    # related = same contirbutor, same cart
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
    instance.calc_clr_round()
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


        if 'hide_wallet_address' in package:
            profile.hide_wallet_address = bool(package.get('hide_wallet_address', False))
            profile.save()

        if 'anonymize_gitcoin_grants_contributions' in package:
            profile.anonymize_gitcoin_grants_contributions = bool(package.get('anonymize_gitcoin_grants_contributions', False))
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
def predict_clr(save_to_db=False, from_date=None, clr_round=None, network='mainnet', only_grant_pk=None):
    # setup
    clr_calc_start_time = timezone.now()
    debug_output = []

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)
    uv_threshold = float(clr_round.unverified_threshold)

    grants, contributions = fetch_data(clr_round, network)

    if contributions.count() == 0:
        print(f'No Contributions for CLR {clr_round.round_num}. Exiting')
        return

    grant_contributions_curr = populate_data_for_clr(grants, contributions, clr_round)

    if only_grant_pk:
        grants = grants.filter(pk=only_grant_pk)

    # calculate clr given additional donations
    for grant in grants:
        # five potential additional donations plus the base case of 0
        potential_donations = [0, 1, 10, 100, 1000, 10000]
        potential_clr = []

        for amount in potential_donations:
            # calculate clr with each additional donation and save to grants model
            # print(f'using {total_pot_close}')
            predicted_clr, grants_clr, _, _ = calculate_clr_for_donation(
                grant,
                amount,
                grant_contributions_curr,
                total_pot,
                v_threshold,
                uv_threshold
            )
            potential_clr.append(predicted_clr)

        if save_to_db:
            _grant = Grant.objects.get(pk=grant.pk)
            clr_prediction_curve = list(zip(potential_donations, potential_clr))
            base = clr_prediction_curve[0][1]
            _grant.last_clr_calc_date = timezone.now()
            _grant.next_clr_calc_date = timezone.now() + timezone.timedelta(minutes=20)

            can_estimate = True if base or clr_prediction_curve[1][1] or clr_prediction_curve[2][1] or clr_prediction_curve[3][1] else False

            if can_estimate :
                clr_prediction_curve  = [[ele[0], ele[1], ele[1] - base] for ele in clr_prediction_curve ]
            else:
                clr_prediction_curve = [[0.0, 0.0, 0.0] for x in range(0, 6)]

            JSONStore.objects.create(
                created_on=from_date,
                view='clr_contribution',
                key=f'{grant.id}',
                data=clr_prediction_curve,
            )
            clr_round.record_clr_prediction_curve(_grant, clr_prediction_curve)
            
            try:
                if clr_prediction_curve[0][1]:
                    Stat.objects.create(
                        created_on=from_date,
                        key=_grant.title[0:43] + "_match",
                        val=clr_prediction_curve[0][1],
                        )
                    max_twitter_followers = max(_grant.twitter_handle_1_follower_count, _grant.twitter_handle_2_follower_count)
                    if max_twitter_followers:
                        Stat.objects.create(
                            created_on=from_date,
                            key=_grant.title[0:43] + "_admt1",
                            val=int(100 * clr_prediction_curve[0][1]/max_twitter_followers),
                            )

                if _grant.positive_round_contributor_count:
                    Stat.objects.create(
                        created_on=from_date,
                        key=_grant.title[0:43] + "_pctrbs",
                        val=_grant.positive_round_contributor_count,
                        )
                if _grant.amount_received_in_round:
                    Stat.objects.create(
                        created_on=from_date,
                        key=_grant.title[0:43] + "_amt",
                        val=_grant.amount_received_in_round,
                        )
            except:
                pass

            if from_date > (clr_calc_start_time - timezone.timedelta(hours=1)):
                _grant.save()

        debug_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})

    try :
        Stat.objects.create(
            key= clr_type + '_grants_round_6_saturation',
            val=int(CLR_PERCENTAGE_DISTRIBUTED),
        )
    except:
        pass

    return debug_output


@app.shared_task(bind=True, max_retries=3)
def process_grant_creation_email(self, grant_id, profile_id):
    grant = Grant.objects.get(pk=grant_id)
    profile = Profile.objects.get(pk=profile_id)

    new_grant(grant, profile)
