'''
    Copyright (C) 2019 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
import logging
import time
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty
from marketing.mails import new_bounty_daily
from marketing.models import EmailSubscriber
from marketing.utils import should_suppress_notification_email
from townsquare.utils import is_email_townsquare_enabled

warnings.filterwarnings("ignore")

override_in_dev = True

def validate_email(email):

    import re
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):
        return True
    return False

def get_bounties_for_keywords(keywords, hours_back):
    new_bounties_pks = []
    all_bounties_pks = []

    new_bounty_cutoff = (timezone.now() - timezone.timedelta(hours=hours_back))
    all_bounty_cutoff = (timezone.now() - timezone.timedelta(days=60))

    for keyword in keywords:
        relevant_bounties = Bounty.objects.current().filter(
            network='mainnet',
            idx_status__in=['open'],
        ).keyword(keyword).exclude(bounty_reserved_for_user__isnull=False)
        for bounty in relevant_bounties.filter(web3_created__gt=new_bounty_cutoff):
            new_bounties_pks.append(bounty.pk)
        for bounty in relevant_bounties.filter(web3_created__gt=all_bounty_cutoff):
            all_bounties_pks.append(bounty.pk)
    new_bounties = Bounty.objects.filter(pk__in=new_bounties_pks).order_by('-_val_usd_db')
    all_bounties = Bounty.objects.filter(pk__in=all_bounties_pks).exclude(pk__in=new_bounties_pks).order_by('-_val_usd_db')

    new_bounties = new_bounties.order_by('-admin_mark_as_remarket_ready')
    all_bounties = all_bounties.order_by('-admin_mark_as_remarket_ready')

    return new_bounties, all_bounties


class Command(BaseCommand):

    help = 'sends new_bounty_daily _emails'

    def handle(self, *args, **options):
        if settings.DEBUG and not override_in_dev:
            print("not active in non prod environments")
            return
        hours_back = 24
        eses = EmailSubscriber.objects.filter(active=True).distinct('email').order_by('-email')
        counter_eval_total = 0
        counter_total = 0
        counter_sent = 0
        start_time = time.time()
        total_count = eses.count()
        print("got {} emails".format(total_count))
        for es in eses:
            try:
                counter_eval_total += 1
                if should_suppress_notification_email(es.email, 'new_bounty_notifications'):
                    continue
                # prep
                now = timezone.now()
                to_email = es.email
                keywords = es.keywords
                town_square_enabled = is_email_townsquare_enabled(to_email)
                should_eval = keywords or town_square_enabled
                if not should_eval:
                    continue
                if not validate_email(to_email):
                    continue
                counter_total += 1
                new_bounties, all_bounties = get_bounties_for_keywords(keywords, hours_back)
                featured_bounties = Bounty.objects.current().filter(
                    network='mainnet', idx_status='open',
                    expires_date__gt=now).order_by('metadata__hyper_tweet_counter')[:2]

                # stats
                speed = round((time.time() - start_time) / counter_eval_total, 2)
                ETA = round((total_count - counter_eval_total) / speed / 3600, 1)
                print(f"{counter_sent} sent/{counter_total} enabled/{counter_eval_total} evaluated, {speed}/s, ETA:{ETA}h, working on {to_email} ")

                # send
                should_send = new_bounties.count() or town_square_enabled
                #should_send = new_bounties.count()
                if should_send:
                    #print(f"sending to {to_email}")
                    new_bounty_daily(new_bounties, all_bounties, [to_email], featured_bounties)
                    #print(f"/sent to {to_email}")
                    counter_sent += 1
            except Exception as e:
                logging.exception(e)
                print(e)
