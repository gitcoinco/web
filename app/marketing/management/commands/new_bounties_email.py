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

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty
from marketing.mails import new_bounty_daily
from marketing.models import EmailSubscriber
from townsquare.utils import is_email_townsquare_enabled

import warnings

warnings.filterwarnings("ignore")

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
        if settings.DEBUG:
            print("not active in non prod environments")
            return
        hours_back = 24
        eses = EmailSubscriber.objects.filter(active=True).distinct('email')
        counter_grant_total = 0
        counter_total = 0
        counter_sent = 0
        print("got {} emails".format(eses.count()))
        for es in eses:
            try:
                counter_grant_total += 1
                to_email = es.email
                keywords = es.keywords
                town_square_enabled = is_email_townsquare_enabled(to_email)
                should_eval = keywords or town_square_enabled
                if not should_eval:
                    continue
                counter_total += 1
                new_bounties, all_bounties = get_bounties_for_keywords(keywords, hours_back)
                print("{}/{}/{}) {}/{}: got {} new bounties & {} all bounties".format(counter_sent, counter_total, counter_grant_total, to_email, keywords, new_bounties.count(), all_bounties.count()))
                should_send = new_bounties.count() or town_square_enabled
                #should_send = new_bounties.count()
                if should_send:
                    print(f"sending to {to_email}")
                    new_bounty_daily(new_bounties, all_bounties, [to_email])
                    print(f"/sent to {to_email}")
                    counter_sent += 1
            except Exception as e:
                logging.exception(e)
                print(e)
