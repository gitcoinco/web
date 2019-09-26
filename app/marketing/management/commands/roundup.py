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
import time
import warnings

from django.core.management.base import BaseCommand

from marketing.mails import weekly_roundup
from marketing.models import EmailSubscriber

warnings.filterwarnings("ignore", category=DeprecationWarning)


check_already_sent = False


def is_already_sent_this_week(email):
    from marketing.models import EmailEvent
    from django.utils import timezone
    then = timezone.now() - timezone.timedelta(hours=12)
    QS = EmailEvent.objects.filter(created_on__gt=then)
    QS = QS.filter(category__contains='weekly_roundup', email__iexact=email, event='processed')
    return QS.exists()


class Command(BaseCommand):

    help = 'the weekly roundup emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '-live', '--live',
            action='store_true',
            dest='live',
            default=False,
            help='Actually Send the emails'
        )
        parser.add_argument(
            '--exclude_startswith',
            dest='exclude_startswith',
            type=str,
            default=None,
            help="exclude_startswith (optional)",
        )
        parser.add_argument(
            '--filter_startswith',
            dest='filter_startswith',
            type=str,
            default=None,
            help="filter_startswith (optional)",
        )
        parser.add_argument(
            '--start_counter',
            dest='start_counter',
            type=int,
            default=0,
            help="start_counter (optional)",
        )

    def handle(self, *args, **options):

        exclude_startswith = options['exclude_startswith']
        filter_startswith = options['filter_startswith']
        start_counter = options['start_counter']

        queryset = EmailSubscriber.objects.all()
        if exclude_startswith:
            queryset = queryset.exclude(email__startswith=exclude_startswith)
        if filter_startswith:
            queryset = queryset.filter(email__startswith=filter_startswith)
        queryset = queryset.order_by('email')
        email_list = list(set(queryset.values_list('email', flat=True)))
        # list.sort(email_list)

        print("got {} emails".format(len(email_list)))

        counter = 0
        for to_email in email_list:
            counter += 1

            # skip any that are below the start counter
            if counter < start_counter:
                continue

            print("-sending {} / {}".format(counter, to_email))
            if options['live']:
                try:
                    if check_already_sent and is_already_sent_this_week(to_email):
                        print(' -- already sent')
                    else:
                        weekly_roundup([to_email])
                        time.sleep(1)
                except Exception as e:
                    print(e)
                    time.sleep(5)
