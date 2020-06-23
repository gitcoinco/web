from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from app.services import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from chat.tasks import create_channel
from dashboard.models import Activity, Bounty, ObjectView, Profile
from marketing.mails import func_name, grant_update_email, send_mail
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

    tasks.append(
        create_channel.si({
            'team_id': team_id,
            'channel_name': f'bounty-{new_bounty.id}',
            'channel_display_name': f'bounty-{new_bounty.id}'
        }, new_bounty.id)
    )

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


@app.shared_task(bind=True)
def maybe_market_to_user_slack(self, bounty_pk, event_name, retry: bool = True) -> None:
    """
    :param self:
    :param bounty_pk:
    :param event_name:
    :return:
    """
    with redis.lock("maybe_market_to_user_slack:bounty", timeout=LOCK_TIMEOUT):
        bounty = Bounty.objects.get(pk=bounty_pk)
        from dashboard.notifications import maybe_market_to_user_slack_helper
        maybe_market_to_user_slack_helper(bounty, event_name)


@app.shared_task(bind=True, max_retries=3)
def grant_update_email_task(self, pk, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """
    activity = Activity.objects.get(pk=pk)
    grant_update_email(activity)

    from django.utils import timezone
    grant = activity.grant
    grant.last_update = timezone.now()
    grant.save()


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
    user = None
    if user_id:
        user = User.objects.get(pk=user_id)
    redis = RedisService().redis
    for pk in pks:
        key = f"{content_type}_{pk}"
        print(key)
        result = redis.incr(key)
        if pk and view_type == 'individual':
            try:
                ObjectView.objects.create(
                    viewer=user,
                    target_id=pk,
                    target_type=ContentType.objects.filter(model=content_type).first(),
                    view_type=view_type,
                    )
            except:
                pass # fix for https://sentry.io/organizations/gitcoin/issues/1715509732/
