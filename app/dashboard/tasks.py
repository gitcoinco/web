import csv
import json
import math
import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.utils import timezone

from app.services import RedisService
from app.utils import get_location_from_ip
from celery import app, group
from celery.utils.log import get_task_logger
from dashboard.models import Activity, Bounty, Earning, ObjectView, Profile, TransactionHistory, UserAction
from dashboard.utils import get_tx_status_and_details
from economy.models import EncodeAnything
from marketing.mails import func_name, grant_update_email, send_mail
from proxy.views import proxy_view
from retail.emails import render_share_bounty

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2


@app.shared_task(bind=True, max_retries=3)
def bounty_on_create(self, team_id, new_bounty, retry: bool = True) -> None:
    # what has to happen that we want to chain data from one another together
    # from chat.tasks import create_channel

    tasks = list()

    # what has to happen that we can issue without a dependency from any subtasks?

    # look up users in your tribe invite them to the newly issued bounty

    tasks.append(
        bounty_emails.si([], "", "", "", False)
    )

    res = group(tasks)

    res.ready()


@app.shared_task(bind=True, max_retries=3)
def bounty_emails(self, emails, msg, profile_handle, invite_url=None, kudos_invite=False, retry: bool = True) -> None:
    """
    :param self:
    :param emails:
    :param msg:
    :param profile_handle:
    :param invite_url:
    :param kudos_invite:
    :return:
    """
    with redis.lock("tasks:bounty_email:%s" % invite_url, timeout=LOCK_TIMEOUT):
        # need to look at how to send bulk emails with SG
        profile = Profile.objects.get(handle=profile_handle.lower())
        try:
            for email in emails:
                to_email = email
                from_email = settings.CONTACT_EMAIL
                subject = "You have been invited to work on a bounty."
                html, text = render_share_bounty(to_email, msg, profile, invite_url, kudos_invite)
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name=f"@{profile.handle}",
                    categories=['transactional', func_name()],
                )

        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(countdown=30)
        except Exception as e:
            logger.error(str(e))

@app.shared_task(bind=True, max_retries=3)
def export_search_to_csv(self, body, user_handle, retry:bool = True) -> None:


    CSV_HEADER = [
        'profile_id',
        'join_date',
        'github_created_at',
        'first_name',
        'last_name',
        'email',
        'handle',
        'sms_verification',
        'persona',
        'rank_coder',
        'rank_funder',
        'num_hacks_joined',
        'which_hacks_joined',
        'hack_work_starts',
        'hack_work_submits',
        'hack_work_start_orgs',
        'hack_work_submit_orgs',
        'bounty_work_starts',
        'bounty_work_submits',
        'hack_started_feature',
        'hack_started_code_review',
        'hack_started_security',
        'hack_started_design',
        'hack_started_documentation',
        'hack_started_bug',
        'hack_started_other',
        'hack_started_improvement',
        'started_feature',
        'started_code_review',
        'started_security',
        'started_design',
        'started_documentation',
        'started_bug',
        'started_other',
        'started_improvement',
        'submitted_feature',
        'submitted_code_review',
        'submitted_security',
        'submitted_design',
        'submitted_documentation',
        'submitted_bug',
        'submitted_other',
        'submitted_improvement',
        'bounty_earnings',
        'bounty_work_start_orgs',
        'bounty_work_submit_orgs',
        'kudos_sends',
        'kudos_receives',
        'hack_winner_kudos_received',
        'grants_opened',
        'grant_contributed',
        'grant_contributions',
        'grant_contribution_amount',
        'num_actions',
        'action_points',
        'avg_points_per_action',
        'last_action_on',
        'keywords',
        'activity_level',
        'reliability',
        'average_rating',
        'longest_streak',
        'earnings_count',
        'follower_count',
        'following_count',
        'num_repeated_relationships',
        'verification_status'
    ]

    user_profile = Profile.objects.get(handle=user_handle)

    PAGE_SIZE = 1000
    proxy_req = HttpRequest()
    proxy_req.method = 'GET'
    remote_url = f'{settings.HAYSTACK_ELASTIC_SEARCH_URL}/haystack/modelresult/_search'

    query_data = json.loads(body)
    proxy_request = proxy_view(proxy_req, remote_url, {'data': body})
    proxy_json_str = proxy_request.content.decode('utf-8')
    proxy_body = json.loads(proxy_json_str)
    if not proxy_body['timed_out']:
        total_hits = proxy_body['hits']['total']
        hits = proxy_body['hits']['hits']
        finished = False
        output = []
        results = []
        if total_hits < PAGE_SIZE:
            finished = True
            results = hits

        if not finished:

            max_loops = math.ceil(total_hits / PAGE_SIZE)
            for x in range(0, max_loops):
                new_body = query_data
                new_body['from'] = 0 if x is 0 else (PAGE_SIZE * x) + 1
                new_body['size'] = PAGE_SIZE
                new_body = json.dumps(new_body)
                proxy_request = proxy_view(proxy_req, remote_url, {'data': new_body})
                proxy_json_str = proxy_request.content.decode('utf-8')
                proxy_body = json.loads(proxy_json_str)
                hits = proxy_body['hits']['hits']
                results = results + hits

        for result in results:
            source = result['_source']
            row_item = {}
            for k in source.copy():

                new_column = k.replace('_exact', '')

                if new_column in CSV_HEADER:
                    row_item[new_column] = source[k]
            output.append(row_item)
        now = datetime.now()
        csv_file_path = f'/tmp/user-directory-export-{user_profile.handle}-{now}.csv'
        try:
            with open(csv_file_path, 'w', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADER)
                writer.writeheader()
                writer.writerows(output)
        except IOError:
            print("I/O error")
        if os.path.isfile(csv_file_path):

            to_email = user_profile.user.email
            from_email = settings.CONTACT_EMAIL

            subject = "Your exported user directory csv is attached"
            html = text = f'Your exported {csv_file_path.replace("/tmp/", "")} is attached.'
            send_mail(
                from_email,
                to_email,
                subject,
                text,
                html,
                from_name=f"@{user_profile.handle}",
                categories=['transactional'],
                csv=csv_file_path
            )

@app.shared_task(bind=True, max_retries=3)
def profile_dict(self, pk, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """
    if isinstance(pk, list):
        pk = pk[0]
    with redis.lock("tasks:profile_dict:%s" % pk, timeout=LOCK_TIMEOUT):
        profile = Profile.objects.get(pk=pk)
        if profile.frontend_calc_stale:
            profile.calculate_all()
            profile.save()


@app.shared_task(bind=True, max_retries=3)
def update_trust_bonus(self, pk):
    """
    :param self:
    :param pk:
    :return:
    """
    # returns a percentage trust bonus, for this current user.
    # trust bonus starts at 50% and compounds for every new verification added
    # to a max of 150%
    tb = 0.5
    profile = Profile.objects.get(pk=pk)
    if profile.is_poh_verified:
        tb += 0.50
    if profile.is_brightid_verified:
        tb += 0.50
    if profile.is_idena_verified:
        tb += 0.50
    if profile.is_poap_verified:
        tb += 0.25
    if profile.is_ens_verified:
        tb += 0.25
    if profile.sms_verification:
        tb += 0.15
    if profile.is_google_verified:
        tb += 0.15
    if profile.is_twitter_verified:
        tb += 0.15
    if profile.is_facebook_verified:
        tb += 0.15
    # if profile.is_duniter_verified:
    #     tb *= 1.001
    qd_tb = 0
    for player in profile.players.all():
        new_score = 0
        if player.tokens_in:
            new_score = min(player.tokens_in / 100, 0.20)
        qd_tb = max(qd_tb, new_score)

    # cap the trust_bonus score at 1.5
    tb = min(1.5, tb)

    print("Saving - %s - %s - %s" % (profile.handle, profile.trust_bonus, tb))

    # save the new score
    if profile.trust_bonus != tb:
        profile.trust_bonus = tb
        profile.save()


@app.shared_task(bind=True, soft_time_limit=600, time_limit=660, max_retries=3)
def grant_update_email_task(self, pk, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """
    activity = Activity.objects.get(pk=pk)
    grant_update_email(activity)


@app.shared_task(bind=True)
def m2m_changed_interested(self, bounty_pk, retry: bool = True) -> None:
    """
    :param self:
    :param bounty_pk:
    :return:
    """
    with redis.lock("m2m_changed_interested:bounty", timeout=LOCK_TIMEOUT):
        bounty = Bounty.objects.get(pk=bounty_pk)
        from dashboard.notifications import maybe_market_to_github
        maybe_market_to_github(bounty, 'work_started',
                               profile_pairs=bounty.profile_pairs)



@app.shared_task(bind=True, max_retries=1)
def increment_view_count(self, pks, content_type, user_id, view_type, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :param content_type:
    :param user_id:
    :param view_type:
    :return:
    """

    individual_storage = False # TODO: Change back to true IFF we figure out how to manage storage of this table
    user = None
    if user_id:
        user = User.objects.get(pk=user_id)
    redis = RedisService().redis
    for pk in pks:
        key = f"{content_type}_{pk}"
        print(key)
        result = redis.incr(key)
        if pk and view_type == 'individual' and individual_storage:
            try:
                ObjectView.objects.create(
                    viewer=user,
                    target_id=pk,
                    target_type=ContentType.objects.filter(model=content_type).first(),
                    view_type=view_type,
                    )
            except:
                pass # fix for https://sentry.io/organizations/gitcoin/issues/1715509732/


@app.shared_task(bind=True, max_retries=1)
def sync_profile(self, handle, user_pk, hide_profile, retry: bool = True) -> None:
    from app.utils import actually_sync_profile
    user = User.objects.filter(pk=user_pk).first() if user_pk else None
    actually_sync_profile(handle, user=user, hide_profile=hide_profile)


@app.shared_task(bind=True, max_retries=1)
def recalculate_earning(self, pk, retry: bool = True) -> None:
    from dashboard.models import Earning
    earning = Earning.objects.get(pk=pk)
    src = earning.source
    src.save()


@app.shared_task(bind=True, max_retries=1)
def record_visit(self, user_pk, profile_pk, ip_address, visitorId, useragent, referrer, path, session_key, utm, retry: bool = True) -> None:
    """
    :param self: Self
    :param user_pk: user primary
    :param profile_pk: profile primary
    :param ip_address: get_ip(request)
    :param visitorId: request.COOKIES.get("visitorId", None)
    :param useragent: request.META['HTTP_USER_AGENT']
    :param referrer: request.META.get('HTTP_REFERER', None)
    :param path: request.META.get('PATH_INFO', None)
    :param session_key: request.session._session_key
    :param utm: _get_utm_from_cookie(request)
    :return: None
    """

    user = User.objects.filter(pk=user_pk).first() if user_pk else None
    profile = Profile.objects.filter(pk=profile_pk).first() if profile_pk else None
    if user and profile:
        try:
            profile.last_visit = timezone.now()
            profile.save()
        except Exception as e:
            logger.exception(e)

        # enqueue profile_dict recalc
        profile_dict.delay(profile.pk)

        try:
            metadata = {
                'visitorId': visitorId,
                'useragent': useragent,
                'referrer': referrer,
                'path': path,
                'session_key': session_key,
            }
            UserAction.objects.create(
                user=user,
                profile=profile,
                action='Visit',
                location_data=get_location_from_ip(ip_address),
                ip_address=ip_address,
                utm=utm,
                metadata=metadata,
            )

            # if the user is from a bad jurisdiction, block themm.
            # or is named after an entity that is banned, block them
            from dashboard.utils import should_be_blocked
            if should_be_blocked(profile.handle):
                from dashboard.models import BlockedUser
                BlockedUser.objects.create(
                    handle=profile.handle,
                    comments='should_be_blocked',
                    active=True,
                    user=user,
                    )
        except Exception as e:
            logger.exception(e)


@app.shared_task(bind=True, max_retries=1)
def record_join(self, profile_pk, retry: bool = True) -> None:
    """
    :param self: Self
    :param profile_pk: profile primary
    :return: None
    """

    profile = Profile.objects.filter(pk=profile_pk).first() if profile_pk else None
    if profile:
        try:
            activity = Activity.objects.create(profile=profile, activity_type='joined')
            activity.populate_profile_activity_index()
        except Exception as e:
            logger.exception(e)


@app.shared_task(bind=True, max_retries=3)
def save_tx_status_and_details(self, earning_pk, chain='std'):
    """
    :param self: Self
    :param txid: transaction id
    :param network: the network to pass to web3
    :param created_on: time used to detect if the tx was dropped
    :param chain: chain to pass to web3
    :return: None
    """
    earning = Earning.objects.filter(pk=earning_pk).first()
    txid = earning.txid
    network = earning.network
    created_on = earning.created_on
    status, timestamp, tx = get_tx_status_and_details(txid, network, created_on, chain)
    if status not in ['unknown', 'pending']:
        tx = tx if tx else {}
        TransactionHistory.objects.create(
            earning=earning,
            status=status,
            payload=json.loads(json.dumps(dict(tx), cls=EncodeAnything)),
            network=network,
            txid=txid,
            captured_at=timezone.now(),
        )
