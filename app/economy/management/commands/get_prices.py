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


