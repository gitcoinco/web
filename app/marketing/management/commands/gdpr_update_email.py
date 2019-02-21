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

from marketing.mails import gdpr_update
from marketing.models import EmailSubscriber

warnings.filterwarnings("ignore", category=DeprecationWarning)


class Command(BaseCommand):

    help = 'the gdpr policy update email'

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

    def handle(self, *args, **options):
        exclude_startswith = options['exclude_startswith']
        filter_startswith = options['filter_startswith']

        queryset = EmailSubscriber.objects.filter(newsletter=True)
        if exclude_startswith:
            queryset = queryset.exclude(email__startswith=exclude_startswith)
        if filter_startswith:
            queryset = queryset.filter(email__startswith=filter_startswith)
        queryset = queryset.order_by('email')
        email_list = set(queryset.values_list('email', flat=True))

        print(f'got {len(email_list)} emails')

        counter = 0
        for to_email in email_list:
            counter += 1
            print(f'-sending {counter} / {to_email}')
            if options['live']:
                try:
                    gdpr_update([to_email])
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    time.sleep(5)
