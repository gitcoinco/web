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
from django.utils.crypto import get_random_string

from dashboard.models import CoinRedemption


class Command(BaseCommand):
    help = 'generates some coin redemption shortcodes'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)
        parser.add_argument('network', type=str)
        parser.add_argument('token_name', type=str)
        parser.add_argument('contract_address', type=str)
        parser.add_argument('amount', type=int)
        parser.add_argument('expires_date', type=int)

    def handle(self, *args, **options):
        for i in range(0, options['count']):
            shortcode = get_random_string(8)
            cr = CoinRedemption.objects.create(
                shortcode=shortcode,
                url='https://gitcoin.co/coin/redeem/' + shortcode,
                network=options['network'],
                token_name=options['token_name'],
                contract_address=options['contract_address'],
                amount=options['amount'],
                expires_date=timezone.now() + timezone.timedelta(seconds=options['expires_date'])
            )

            print("https://gitcoin.co/coin/redeem/" + cr.shortcode)
