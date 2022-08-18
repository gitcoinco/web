import csv
import json
import math
import os
from datetime import datetime
from functools import reduce
from operator import add
from pprint import pformat

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone

from app.services import RedisService
from app.utils import get_location_from_ip
from celery import app, group
from celery.utils.log import get_task_logger
from dashboard.models import (
    Activity, Bounty, Earning, ObjectView, Passport, PassportStamp, Profile, TransactionHistory, UserAction,
)
from dashboard.utils import get_tx_status_and_details
from economy.models import EncodeAnything
from grants.models import GR15TrustScore
from marketing.mails import func_name, grant_update_email, send_mail
from proxy.views import proxy_view
from retail.emails import render_share_bounty

from .passport_reader import SCORER_SERVICE_WEIGHTS, TRUSTED_IAM_ISSUER, get_passport, get_stream_ids

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

    if settings.FLUSH_QUEUE:
        return

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
    with redis.lock(f"m2m_changed_interested:bounty:{bounty_pk}", timeout=LOCK_TIMEOUT):
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

    if settings.FLUSH_QUEUE:
        return

    from app.utils import actually_sync_profile
    user = User.objects.filter(pk=user_pk).first() if user_pk else None
    actually_sync_profile(handle, user=user, hide_profile=hide_profile)


@app.shared_task(bind=True, max_retries=1)
def recalculate_earning(self, pk, retry: bool = True) -> None:

    if settings.FLUSH_QUEUE:
        return

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

    if settings.FLUSH_QUEUE:
        return

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

    # There seems to be a race condition, this is task is sometimes
    # executed in parallel for the same profile. And this leads to an integrity
    # error (becasue Activity.objects.create also performs delete operations in a
    # post_save signal)
    # To avoid the integrity error we execute this operation in a transaction
    if settings.FLUSH_QUEUE:
        return

    with transaction.atomic():
        profile = Profile.objects.filter(pk=profile_pk).first() if profile_pk else None
        if profile:
            try:
                activity = Activity.objects.create(profile=profile, activity_type='joined')
                activity.populate_activity_index()
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


@app.shared_task
def calculate_trust_bonus(user_id, did, address):
    """
    :param self: Self
    :param user_id: the user_id
    :param did: the did for the passport
    :return: None
    """

    # delay import as this is only available in celery envs
    import didkit

    try:
        # Verify that this DID is not associated to any other profile.
        # We want to avoid the same user creating multiple accounts and re-using the same did
        duplicates = Passport.objects.exclude(user_id=user_id).filter(did=did)

        # Duplicate DID
        if len(duplicates) > 0:
            raise Exception(f"The DID '{did}' is already associated with another users profile.")

        # Pull streamIds from Ceramic Account associated with DID
        stream_ids = get_stream_ids(did)

        # No Ceramic Account found for user
        if not stream_ids:
            raise Exception(f"No Ceramic Account found for '{did}'")

        # check account against did
        is_owner = did.lower() == f"did:pkh:eip155:1:{address.lower()}"

        # Invalid owner
        if not is_owner:
            raise Exception(f"Bad owner when checking did '{did}'")

        # Retrieve DIDs Passport from Ceramic
        passport = get_passport(stream_ids=stream_ids)

        # No Passport discovered
        if not passport:
            raise Exception(f"No Passport discovered for '{did}'")

        # Build a dict like
        #    {
        #       'TRUSTED_IAM_ISSUER#Poh': {
        #         'match_percent': 0.50,
        #         'is_verified': 0  # The user needs at least one verification of this type to get the match_percent
        #     },
        #     ...
        # }
        matched_services = {
            s['ref']: {
                'match_percent': s['match_percent'] / 100.0,
                'is_verified': 0,
            } for s in SCORER_SERVICE_WEIGHTS
        }

        # We verify if the user has a paspsort or not
        # If yes, and the passport has a different DID we delete it (this will also delete the linked stamps)
        # else we update the existing passport
        db_passport = None
        try:
            db_passport = Passport.objects.get(user_id=user_id)

            if db_passport.did != did:
                # The user is linking his passport to a new did (new ETH account)
                db_passport.delete()
                db_passport = None
        except Passport.DoesNotExist:
            pass

        if not db_passport:
            db_passport = Passport(user_id=user_id, did=did, passport=passport)
            db_passport.save()
        else:
            db_passport.did = did
            db_passport.passport = passport
            db_passport.save()

        stamp_validation_list = []
        # Check the validity of each stamp in the passport
        for stamp in passport['stamps']:
            try:
                if stamp and stamp['credential'] and stamp["provider"]:
                    service_key = f"{TRUSTED_IAM_ISSUER}#{stamp['provider']}"

                    if service_key not in matched_services:
                        msg = "Ignoring service with key %s in trust bonus calculation for DID %s" % (service_key, did)
                        logger.warning(msg)
                    else:
                        stamp_validation = {
                            "provider": stamp["provider"],
                            "is_verified": False,
                            "errors": []
                        }
                        stamp_validation_list.append(stamp_validation)

                        # get the user credential ID, this will have the form: "did:ethr:0x...#POAP"
                        subject_id = stamp["credential"]["credentialSubject"]["id"]

                        # the subjectId must match the users DID
                        is_subject_valid = subject_id.lower() == did.lower()

                        stamp_expiration_date = stamp["credential"]["expirationDate"]
                        # the stamp must not have expired before being registered (when expiry comes around, should we expire the stamp on the scorer side?)
                        try:
                            is_stamp_expired = datetime.strptime(stamp_expiration_date, "%Y-%m-%dT%H:%M:%S.%fZ") < datetime.now()
                        except:
                            # In some cases the microseconds are missing in the timestamp (has been encountered in production)
                            is_stamp_expired = datetime.strptime(stamp_expiration_date, "%Y-%m-%dT%H:%M:%SZ") < datetime.now()


                        # the stamp must be issued by the trusted IAM server
                        is_issued_by_iam = stamp["credential"]["issuer"] == TRUSTED_IAM_ISSUER

                        # check that the provider matches the provider in the VC
                        is_for_provider = stamp["provider"] == stamp["credential"]["credentialSubject"]["provider"]

                        if not is_subject_valid:
                            msg = "Invalid stamp subject: %s != %s" %( subject_id, did)
                            stamp_validation["errors"].append(msg)
                            logger.error(msg)

                        if is_stamp_expired:
                            mag = "Expired stamp (%s): %s" % ( subject_id, stamp["credential"]["expirationDate"])
                            stamp_validation["errors"].append(msg)
                            logger.error(msg)

                        if not is_issued_by_iam:
                            msg = "Stamp issuer missmatch: '%s' != '%s'" %( TRUSTED_IAM_ISSUER, stamp["credential"]["issuer"])
                            stamp_validation["errors"].append(msg)
                            logger.error(msg)

                        if not is_for_provider:
                            msg = "Stamp provider missmatch: '%s' != '%s' " % ( stamp["provider"], stamp["credential"]["credentialSubject"]["provider"])
                            stamp_validation["errors"].append(msg)
                            logger.error(msg)

                        if is_subject_valid and not is_stamp_expired and is_issued_by_iam and is_for_provider:
                            # Get the stamp ID, and register it with our records
                            # This will be used to ensure that this stamp is not linked to any other user profile
                            stamp_credential = stamp["credential"]
                            stamp_id = stamp_credential["credentialSubject"]["hash"]
                            stamp_provider = stamp_credential["credentialSubject"]["provider"]

                            # if the hash exists in PassportStamps assigned to another user, then this user cannot use it
                            duplicate_stamp_ids = PassportStamp.objects.exclude(user_id=user_id).filter(stamp_id=stamp_id)
                            stamp_id_is_valid = len(duplicate_stamp_ids) == 0

                            if not stamp_id_is_valid:
                                msg = "Duplicate stamp id detected: %s" % (stamp_id, )
                                stamp_validation["errors"].append(msg)
                                logger.error(msg)

                            if stamp_id_is_valid:
                                # Save the stamp id and associate it with the Passport entry
                                stamp_registry = PassportStamp.objects.update_or_create(
                                    user_id=user_id,
                                    stamp_id=stamp_id,
                                    defaults={
                                        "passport": db_passport,
                                        "stamp_credential": stamp_credential,
                                        "stamp_provider": stamp_provider
                                    }
                                )

                                # Proceed with verifying the credential
                                verification = didkit.verifyCredential(json.dumps(stamp["credential"]), '{"proofPurpose":"assertionMethod"}')
                                verification = json.loads(verification)

                                # Check that the credential verified
                                stamp['is_verified'] = (not verification["errors"])

                                # Given a valid stamp - set is_verified and add stamp to returns
                                if stamp['is_verified']:
                                    # The user only needs one verification for a certain provider in order to obtain the score for that provider
                                    matched_services[service_key]['is_verified'] = True
                                    stamp_validation['is_verified'] = True
                                    stamp_validation["match_percent"] = matched_services[service_key]["match_percent"]
            except Exception as e:
                logger.error("Error verifying the stamp: %s. Error: %s", stamp, e, exc_info=True)

        # Calculate the trust score based on the verified stamps
        trust_score = min(1.5, 0.5 + reduce(add, [match["match_percent"] * (1 if match["is_verified"] else 0) for _, match in matched_services.items()]))

        # Save the new trust score into the users profile
        profile = Profile.objects.get(user_id=user_id)
        profile.passport_trust_bonus = trust_score
        profile.passport_trust_bonus_status = "saved"
        profile.passport_trust_bonus_last_updated = timezone.now()
        profile.passport_trust_bonus_stamp_validation = stamp_validation_list
        profile.save()

    except Exception as e:
        # Log the error
        logger.error(e)
        # We expect this verification to throw
        logger.error("Error calculating trust bonus score!", exc_info=True)
        profile = Profile.objects.get(user_id=user_id)
        profile.passport_trust_bonus = profile.passport_trust_bonus or 0.5
        profile.passport_trust_bonus_status = f"Error: {e}"[:255]
        profile.passport_trust_bonus_last_updated = timezone.now()
        profile.passport_trust_bonus_stamp_validation = []
        profile.save()


@app.shared_task
def calculate_trust_bonus_gr15():
    """
    :return: None
    """

    # delay import as this is only available in celery envs
    import pandas as pd
    import datar.all as r
    from datar.core.factory import func_factory

    try:
        @func_factory("agg", "x")
        def my_paste(x):
            return ", ".join(x)

        @func_factory("agg", "x")
        def my_len(x):
            return len(x)


        @func_factory("agg", "x")
        def my_head(x, n=1):
            return x[0:n]

        def compute_trust_scores(gc, stamp_fields, grouping_fields, grouping_fields_1):
            pca_dat = gc >> r.select(~r.f[grouping_fields_1])

            method_combos = (
                gc
                >> r.select(~r.f[grouping_fields])
                >> r.pivot_longer(cols=[stamp_fields], names_to="Authentication", values_to="Value")
                >> r.filter(r.f.Value)
                >> r.group_by(r.f.user_id)
                >> r.summarise(Combo=my_paste(r.f.Authentication), Num=my_len(r.f.Authentication))
                >> r.group_by(r.f.Combo)
                >> r.summarise(Count=r.n(), Num=my_head(r.f.Num))
                >> r.arrange(r.desc(r.f.Count))
                >> r.group_by(r.f.Num)
                >> r.mutate(
                    Prop=r.f.Count / r.sum(r.f.Count),
                    Weight=1 - r.f.Prop,
                    Score=r.f.Weight * (1 / pca_dat.shape[1]) + (r.f.Num / pca_dat.shape[1]),
                )
                >> r.arrange(r.desc(r.f.Num), r.desc(r.f.Count))
            )

            method4_prelim = (
                gc
                >> r.select(~r.f[grouping_fields])
                >> r.pivot_longer(cols=[stamp_fields], names_to="Authentication", values_to="Value")
                >> r.filter(r.f.Value)
                >> r.group_by(r.f.user_id)
                >> r.summarise(Combo=my_paste(r.f.Authentication))
                >> r.left_join(method_combos)
            )

            method4 = gc >> r.select(r.f.user_id) >> r.left_join(method4_prelim)

            method4["Score"].fillna(0, inplace=True)
            method4 = method4[method4["Combo"].notnull()]

            return method4


        stamps = list(PassportStamp.objects.all().values("user_id", "stamp_provider"))
        df = pd.DataFrame(stamps)
        df["stamp_provider"] = df.stamp_provider.str.lower()

        providers = [p for p in df.stamp_provider.unique() if p]

        for p in providers:
            df[p] = 0
            df.loc[df["stamp_provider"] == p, p] = 1

        prepared_df = df.groupby(['user_id']).max()
        prepared_df.reset_index(inplace=True)

        grouping_fields_1 = [
            r.f["user_id"],  
        ]

        grouping_fields = []
        stamp_fields = [r.f[p] for p in providers]

        scores = compute_trust_scores(prepared_df, stamp_fields, grouping_fields, grouping_fields_1)
        print(scores)

        for _index, row in scores.iterrows():
            print(row["user_id"], "==>", row["Score"])

        # Write the results to the DB
        GR15TrustScore.objects.all().delete()

        gr15_trust_scores = [GR15TrustScore(user_id=row["user_id"], score=row["Score"]) for _index, row in scores.iterrows()]
        GR15TrustScore.objects.bulk_create(gr15_trust_scores)

    except Exception as e:
        # Log the error
        logger.error(e)
        # We expect this verification to throw
        logger.error("Error calculating trust bonus score!", exc_info=True)
