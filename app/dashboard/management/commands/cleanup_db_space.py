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

from django.core.management.base import BaseCommand
from django.utils import timezone

from economy.models import ConversionRate
from gas.models import GasGuzzler, GasProfile
from marketing.models import LeaderboardRank, Stat


class Command(BaseCommand):

    help = 'cleans up database objects that are old'

    def get_then(self, days_back=7):
        return timezone.now() - timezone.timedelta(days=days_back)

    def handle(self, *args, **options):

        for model in [GasGuzzler, GasProfile]:
            result = model.objects.filter(
                created_on__lt=self.get_then(7),
                ).exclude(created_on__minute__lt=10).delete()
            print(f'{model}: {result}')

        result = ConversionRate.objects.filter(
                created_on__lt=self.get_then(7),
            ).exclude(
                from_currency='ETH',
                to_currency='USDT',
            ).exclude(
                from_currency='USDT',
                to_currency='ETH'
            ).delete()
        print(f'ConversionRate: {result}')

        result = Stat.objects.filter(
                created_on__lt=self.get_then(7),
            ).exclude(
                created_on__hour=1,
            ).delete()
        print(f'Stat: {result}')

        result = LeaderboardRank.objects.filter(
                created_on__lt=self.get_then(14),
            ).delete()
        print(f'LeaderboardRank: {result}')
