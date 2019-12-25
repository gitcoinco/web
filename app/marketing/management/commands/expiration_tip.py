'''
    Copyright (C) 2019 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Tip
from marketing.mails import tip_email


class Command(BaseCommand):

    help = 'the expiration notifications'

    def handle(self, *args, **options):
        days = [1, 2]
        for day in days:
            tips = Tip.objects.send_success().filter(
                expires_date__lt=(timezone.now() + timezone.timedelta(days=(day+1))),
                expires_date__gte=(timezone.now() + timezone.timedelta(days=day)),
                receive_txid='',
                network='mainnet',
            ).all()
            print('day {} got {} tips'.format(day, tips.count()))
            for t in tips:
                tip_email(t, [t.primary_email], False)
