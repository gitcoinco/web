import csv
import os
import io

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

import marketing.stats as stats
from app.services import RedisService
from celery import app
from celery.utils.log import get_task_logger
from marketing.mails import new_bounty_daily as new_bounty_daily_email
from marketing.mails import weekly_roundup as weekly_roundup_email
from marketing.models import EmailSubscriber
from marketing.common.utils import allowed_to_send_email
from marketing.common.earnings import export_earnings, send_csv, send_download_failure_email

logger = get_task_logger(__name__)

redis = RedisService().redis

rate_limit = '300000/s' if settings.FLUSH_QUEUE or settings.MARKETING_FLUSH_QUEUE else settings.MARKETING_QUEUE_RATE_LIMIT

@app.shared_task(bind=True)
def send_earnings_csv(self, user_pk, export_type):
    user = User.objects.get(pk=user_pk)
    data = export_earnings(export_type, user.profile)
    try:
        send_csv(data=data, user_profile=user.profile)
    except:
        send_download_failure_email(profile)


@app.shared_task(bind=True, rate_limit=rate_limit, soft_time_limit=600, time_limit=660, max_retries=1)
def new_bounty_daily(self, email_subscriber_id, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """

    # dont send emails on this server, dispurse them back into the queue
    if settings.FLUSH_QUEUE:
        return

    if settings.MARKETING_FLUSH_QUEUE:
        return

    # actually do the task
    es = EmailSubscriber.objects.get(pk=email_subscriber_id)

    if allowed_to_send_email(es.email, 'new_bounty_notifications'):
        return

    new_bounty_daily_email(es)


@app.shared_task(bind=True, rate_limit=rate_limit)
def weekly_roundup(self, to_email, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """

    # dont send emails on this server, dispurse them back into the queue
    if settings.MARKETING_FLUSH_QUEUE:
        redis.sadd('weekly_roundup_retry', to_email)
        return

    if settings.FLUSH_QUEUE:
        redis.sadd('weekly_roundup_retry', to_email)
        return

    # actually do the task
    weekly_roundup_email([to_email])


#THROTTLE_S = 0.1
#BUFFER_S = 0.05
#num_users = 50000
#time_limit = num_users * (BUFFER_S + THROTTLE_S)

#@app.shared_task(bind=True, max_retries=1, time_limit=time_limit)
@app.shared_task(bind=True, max_retries=1)
def send_all_weekly_roundup(self, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """
    #import time
    queryset = EmailSubscriber.objects.all()
    email_list = list(set(queryset.values_list('email', flat=True)))
    for to_email in email_list:
        weekly_roundup.delay(to_email)
        #time.sleep(THROTTLE_S)


@app.shared_task(bind=True, max_retries=1)
def get_stats(self, fn):
    f = getattr(stats, fn)
    try:
        f()
    except Exception as e:
        logger.error(str(e))
