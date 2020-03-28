# -*- coding: utf-8 -*-
"""Define the management command to pull new price data for tokens.

Copyright (C) 2020 Gitcoin Core

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

from django.conf import settings
from django.core.management.base import BaseCommand

import ccxt
import cryptocompare as cc
import requests
from dashboard.models import Bounty, Tip
from economy.models import ConversionRate
from grants.models import Contribution
from kudos.models import KudosTransfer
from websocket import create_connection


def stablecoins():
    for to_currency in settings.STABLE_COINS:
        if to_currency == 'to_currency':
            continue
        from_amount = 1
        to_amount = 1
        from_currency = 'USDT'
        ConversionRate.objects.create(
            from_amount=from_amount,
            to_amount=to_amount,
            source='stablecoin',
            from_currency=from_currency,
            to_currency=to_currency)
        print(f'stablecoin: {from_currency}=>{to_currency}:{to_amount}')


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
            print(f'Poloniex: {from_currency}=>{to_currency}:{to_amount}')
        except Exception as e:
            print(e)


def refresh_bounties():
    for bounty in Bounty.objects.all():
        print(f'refreshed {bounty.pk}')
        try:
            bounty._val_usd_db = bounty.value_in_usdt
            bounty._val_usd_db_now = bounty.value_in_usdt_now
            bounty.save()
        except Exception as e:
            print(e)
            bounty._val_usd_db = 0
            bounty._val_usd_db_now = 0
            bounty.save()


def refresh_conv_rate(when, token_name):
    to_currency = 'USDT'
    conversion_rate = ConversionRate.objects.filter(
        from_currency=token_name,
        to_currency=to_currency,
        timestamp=when
    )

    if not conversion_rate:  # historical ConversionRate for the given bounty does not exist yet
        try:
            price = cc.get_historical_price(token_name, to_currency, when)

            to_amount = price[token_name][to_currency]
            ConversionRate.objects.create(
                from_amount=1,
                to_amount=to_amount,
                source='cryptocompare',
                from_currency=token_name,
                to_currency=to_currency,
                timestamp=when,
            )
            print(f'Cryptocompare: {token_name}=>{to_currency}:{to_amount}')
        except Exception as e:
            print(e)


def cryptocompare():
    """Handle pulling market data from CryptoCompare.

    Updates ConversionRates only if data not available.

    """
    for bounty in Bounty.objects.current():
        print(f'CryptoCompare Bounty {bounty.pk}')
        refresh_conv_rate(bounty.web3_created, bounty.token_name)

    for tip in Tip.objects.all():
        print(f'CryptoCompare Tip {tip.pk}')
        refresh_conv_rate(tip.created_on, tip.tokenName)

    for obj in KudosTransfer.objects.all():
        print(f'CryptoCompare KT {obj.pk}')
        refresh_conv_rate(obj.created_on, obj.tokenName)

    for obj in Contribution.objects.all():
        print(f'CryptoCompare GrantContrib {obj.pk}')
        refresh_conv_rate(obj.created_on, obj.subscription.token_symbol)


def uniswap():
    """Hangle pulling market data from Uniswap using its subgraph node on mainnet."""
    pull_uniswap_tokens_only = ['PAN']
    endpoint = 'https://api.thegraph.com/subgraphs/name/graphprotocol/uniswap'
    query_limit = 100
    skip = 0
    # GraphQL query based on the Uniswap API
    # Ref: https://github.com/Uniswap/uniswap-api/blob/master/src/_apollo/queries.ts#L3
    while True:
        query = f"""
          query {{
           exchanges(first: {query_limit}, skip: {skip}, orderBy: ethBalance, orderDirection: desc) {{
            id
            tokenAddress
            tokenSymbol
            tokenName
            price
            lastPrice
            priceUSD
            lastPriceUSD
           }}
         }}
        """
        try:
            rs = requests.post(url=endpoint, json={'query': query})
            if rs.ok:
                json_data = rs.json()
                total_records = len(json_data['data']['exchanges'])
                print(f"Cursor ==> {skip} - Total records ==> {total_records}")
                if total_records == 0:
                    break
                for exchange in json_data['data']['exchanges']:
                    try:
                        token_name = exchange['tokenSymbol']
                        if token_name not in pull_uniswap_tokens_only:
                            continue
                        if float(exchange['price']) == 0.: # Skip exchange pairs with zero value
                            continue
                        if token_name == 'ETH':
                            continue # dont pull ETH/ETH and ETH/USD pricing
                        to_amount = (float(exchange['price']) + float(exchange['lastPrice'])) / 2.
                        ConversionRate.objects.create(
                            from_amount=1,
                            to_amount=to_amount,
                            source='uniswap',
                            from_currency='ETH',
                            to_currency=token_name)
                        print(f'Uniswap: ETH=>{token_name}:{to_amount}')

                        to_amount_usd = (float(exchange['priceUSD']) + float(exchange['lastPriceUSD'])) / 2.
                        ConversionRate.objects.create(
                            from_amount=1,
                            to_amount=to_amount_usd,
                            source='uniswap',
                            from_currency=token_name,
                            to_currency='USDT')
                        print(f'Uniswap: {token_name}=>USDT:{to_amount_usd}')
                    except Exception as e:
                        print(f'Error when storing Uniswap exchange data for token ${token_name}: ${str(e)}')
                skip += query_limit
            else:
                raise Exception(f'Error when requesting Exchange data from Uniswap Graph node: {rs.reason}')
        except Exception as e:
            print(e)


class Command(BaseCommand):
    """Define the management command to update currency conversion rates."""

    help = 'gets prices for all (or... as many as possible) tokens'

    def add_arguments(self, parser):
        parser.add_argument('perform_obj_updates', default='localhost', type=int)

    def handle(self, *args, **options):
        """Get the latest currency rates."""
        stablecoins()

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


        try:
            print('uniswap')
            uniswap()
        except Exception as e:
            print(e)

        if not options['perform_obj_updates']:
            return

        try:
            print('cryptocompare')
            cryptocompare()
        except Exception as e:
            print(e)

        try:
            print('refresh')
            refresh_bounties()
        except Exception as e:
            print(e)
