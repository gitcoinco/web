'''
    Copyright (C) 2021 Gitcoin Core

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

from marketing.models import EmailSubscriber
from marketing.tasks import new_bounty_daily
from marketing.utils import should_suppress_notification_email
from townsquare.utils import is_email_townsquare_enabled

warnings.filterwarnings("ignore")

override_in_dev = True

THROTTLE_S = 0.02


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
        start_time = time.time() - 1
        total_count = eses.count()
        print("got {} emails".format(total_count))
        for es in eses:
            try:
                counter_eval_total += 1
                # KO 21/16/03 - evalute suppression list in queue
                # if should_suppress_notification_email(es.email, 'new_bounty_notifications'):
                #    continue
                
                # prep

                to_email = es.email
                counter_total += 1

                # stats
                speed = counter_total / (time.time() - start_time)
                ETA = round((total_count - counter_total) / speed / 3600, 1)
                print(
                    f"{counter_sent} sent/{counter_total} enabled/ {total_count} total, {round(speed, 2)}/s, ETA:{ETA}h, working on {to_email} ")

                # send
                did_send = new_bounty_daily.delay(es.pk)
                if did_send:
                    counter_sent += 1

                time.sleep(THROTTLE_S)

            except Exception as e:
                logging.exception(e)
                print(e)
