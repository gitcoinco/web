from django.conf import settings

import csv
import os
import marketing.stats as stats
from app.services import RedisService
from celery import app
from celery.utils.log import get_task_logger
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
from marketing.mails import new_bounty_daily as new_bounty_daily_email
from marketing.mails import weekly_roundup as weekly_roundup_email, send_mail
from marketing.models import EmailSubscriber
from marketing.utils import allowed_to_send_email

logger = get_task_logger(__name__)

redis = RedisService().redis

rate_limit = '300000/s' if settings.FLUSH_QUEUE or settings.MARKETING_FLUSH_QUEUE else settings.MARKETING_QUEUE_RATE_LIMIT

@app.shared_task(bind=True)
def export_earnings_to_csv(self, user_pk, export_type):
    user = User.objects.get(pk=user_pk)
    profile = user.profile
    earnings = profile.earnings if export_type == 'earnings' else profile.sent_earnings
    earnings = earnings.filter(network='mainnet').order_by('-created_on')

    path = f'app/assets/tmp/user-{export_type}/{profile}'
    if not os.path.isdir(path):
        os.makedirs(path)
    name = f"{timezone.now().strftime('%Y_%m_%dT%H')}"
    file_path = f'{path}/{name}.csv'

    # import pdb; pdb.set_trace()

    with open(file_path, 'w', encoding='utf-8') as earnings_csv:
        writer = csv.writer(earnings_csv)
        writer.writerow(['test', 'date', 'From', 'From Location', 'To', 'To Location', 'Type', 'Value In USD', 'txid', 'token_name', 'token_value', 'url'])
        for earning in earnings:
            writer.writerow([earning.pk,
                earning.created_on.strftime("%Y-%m-%dT%H:00:00"),
                earning.from_profile.handle if earning.from_profile else '*',
                earning.from_profile.data.get('location', 'Unknown') if earning.from_profile else 'Unknown',
                earning.to_profile.handle,
                earning.to_profile.data.get('location', 'Unknown'),
                earning.source_type_human,
                earning.value_usd,
                earning.txid,
                earning.token_name,
                earning.token_value,
                earning.url,
            ])
    
    to_email = 'jeremy@redsquirrel.com'
    from_email = settings.CONTACT_EMAIL
    subject = "Your exported csv is attached"
    html = text = 'Your exported csv is attached.'
    send_mail(
        from_email,
        to_email,
        subject,
        text,
        html,
        from_name="@jer-sch",
        categories=['transactional'],
        csv=writer
    )

    os.remove(file_path)

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
