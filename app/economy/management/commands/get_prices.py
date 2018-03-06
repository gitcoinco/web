# -*- coding: utf-8 -*-
"""Define the management command to pull new price data for tokens.

Copyright (C) 2018 Gitcoin Core

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

"""
import json

from django.core.management.base import BaseCommand

import ccxt
from dashboard.models import Bounty
from economy.models import ConversionRate
from websocket import create_connection


def etherdelta():
    """Handle pulling market data from Etherdelta."""
    count = 0
    result = ''

    print('Attempting to connect to etherdelta API websocket...')
    ws = create_connection('wss://socket.etherdelta.com/socket.io/?transport=websocket')
    print('Sending getMarket message...')
    ws.send('42["getMarket",{}]')
    print('Sent getMarket message! Waiting on proper response...')

    # Wait for the getMarket response or timeout at 30.
    while (result[:2] != "42" or count > 60):
        result = ws.recv()
        count += 1
        print(count)

    ws.close()  # Close the websocket connection.

    try:
        # Attempt to format the response data.
        market_results = json.loads(result[2:])
        tickers = market_results[1]['returnTicker']
    except ValueError:
        tickers = {}
        print('Failed to retrieve etherdelta ticker data!')

    # etherdelta
    for pair, result in tickers.items():
        from_currency = pair.split('_')[1]
        to_currency = pair.split('_')[0]

        from_amount = 1
        to_amount = (result['bid'] + result['ask']) / 2
        try:
            ConversionRate.objects.create(
                from_amount=from_amount,
                to_amount=to_amount,
                source='etherdelta',
                from_currency=from_currency,
                to_currency=to_currency)
            print(f'Etherdelta: {from_currency}=>{to_currency}:{to_amount}')
        except Exception as e:
            print(e)


def polo():
    """Handle pulling market data from Poloneix."""
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
                to_currency=to_currency)
            print('Poloniex: {}=>{}:{}'.format(from_currency, to_currency, to_amount))
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


class Command(BaseCommand):
    """Define the management command to update currency conversion rates."""

    help = 'gets prices for all (or... as many as possible) tokens'

    def handle(self, *args, **options):
        """Get the latest currency rates."""
        try:
            print('ED')
            etherdelta()
        except Exception as e:
            print(e)

        try:
            print('polo')
            polo()
        except Exception as e:
            print(e)
