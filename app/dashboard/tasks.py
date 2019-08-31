from django.conf import settings

from celery import app
from celery.utils.log import get_task_logger
from app.redis_service import RedisService
from dashboard.models import Profile
from marketing.mails import send_mail, func_name
from retail.emails import render_share_bounty

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2


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
        profile = Profile.objects.get(handle=profile_handle)
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
            print(exc)
            self.retry(30)
