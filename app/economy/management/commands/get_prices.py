'''
    Copyright (C) 2017 Gitcoin Core 

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
from dashboard.models import Bounty
from django.core.management.base import BaseCommand
from economy.models import ConversionRate
import requests
import ccxt


class Command(BaseCommand):

    help = 'gets prices for all (or... as many as possible) tokens'

    def handle(self, *args, **options):

        r = requests.get('https://api.etherdelta.com/returnTicker')
        tickers = r.json()

        #etherdelta
        for pair, result in tickers.items():
            from_currency = pair.split('_')[0]
            to_currency = pair.split('_')[1]

            from_amount = 1
            to_amount = (result['bid'] + result['ask']) / 2
            try:
                ConversionRate.objects.create(
                    from_amount=from_amount,
                    to_amount=to_amount,
                    source='etherdelta',
                    from_currency=from_currency,
                    to_currency=to_currency,
                    )
                print('{}=>{}:{}'.format(from_currency, to_currency, to_amount))
            except Exception as e:
                print(e)

        tickers = ccxt.poloniex().load_markets()
        for pair, result in tickers.items():
            from_currency = pair.split('/')[0]
            to_currency = pair.split('/')[1]

            from_amount = 1
            try:
                to_amount = (float(result['info']['highestBid']) + float(result['info']['lowestAsk'])) / 2
                ConversionRate.objects.create(
                    from_amount=from_amount,
                    to_amount=to_amount,
                    source='poloniex',
                    from_currency=from_currency,
                    to_currency=to_currency,
                    )
                print('{}=>{}:{}'.format(from_currency, to_currency, to_amount))
            except Exception as e:
                print(e)

        for b in Bounty.objects.all():
            print('refreshed {}'.format(b.pk))
            try:
                b._val_usd_db = b.value_in_usdt
                b.save()
            except Exception as e:
                print(e)
                b._val_usd_db = 0
                b.save()


