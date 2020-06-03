from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from app.redis_service import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from marketing.models import EmailSubscriber
from marketing.mails import new_bounty_daily as new_bounty_daily_email, weekly_roundup as weekly_roundup_email

logger = get_task_logger(__name__)

redis = RedisService().redis


@app.shared_task(bind=True, max_retries=1)
def new_bounty_daily(self, email_subscriber_id, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """
    es = EmailSubscriber.objects.get(pk=email_subscriber_id)
    new_bounty_daily_email(es)

@app.shared_task(bind=True, max_retries=1)
def weekly_roundup(self, to_email, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """
    weekly_roundup_email([to_email])
