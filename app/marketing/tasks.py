from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from app.services import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from marketing.mails import new_bounty_daily as new_bounty_daily_email
from marketing.mails import weekly_roundup as weekly_roundup_email
from marketing.models import EmailSubscriber

import socket

logger = get_task_logger(__name__)

redis = RedisService().redis


@app.shared_task(bind=True, rate_limit='2/s')
def new_bounty_daily(self, email_subscriber_id, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """

    # dont send roundup emails on this server, dispurse them back into the queue
    if socket.gethostname() == 'ip-172-31-5-127':
        self.retry(countdown=5)
        return
    # actually do the task
    es = EmailSubscriber.objects.get(pk=email_subscriber_id)
    new_bounty_daily_email(es)

@app.shared_task(bind=True, rate_limit='2/s')
def weekly_roundup(self, to_email, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """

    # dont send roundup emails on this server, dispurse them back into the queue
    if socket.gethostname() == 'ip-172-31-5-127':
        self.retry(countdown=5)
        return
    
    # actually do the task
    weekly_roundup_email([to_email])



@app.shared_task(bind=True, max_retries=1)
def send_all_weekly_roundup(self, retry: bool = True) -> None:
    """
    :param self:
    :param pk:
    :return:
    """
    #THROTTLE_S = 0.005
    #import time
    queryset = EmailSubscriber.objects.all()
    email_list = list(set(queryset.values_list('email', flat=True)))
    for to_email in email_list:
        weekly_roundup.delay(to_email)
        #time.sleep(THROTTLE_S)
