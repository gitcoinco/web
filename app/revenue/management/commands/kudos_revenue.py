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
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from revenue.models import DigitalGoodPurchase

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

DEFAULT_START_BLOCK = 0


def call_etherscan_api(network, params):
    try:
        api_url = f'http://api{f"-{network}" if network != "mainnet" else ""}.etherscan.io/api'
        headers= {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:71.0) Gecko/20100101 Firefox/71.0'}
        rs = requests.get(api_url, params, headers=headers)
        if not rs.ok:
            logger.error(f"* Error while executing API request to Etherscan in kudos_revenue => Error {rs.status_code}: {rs.reason}")
            return []
        rs_json = rs.json()
        if rs_json['message'] != 'OK':
            if type(rs_json['result']) == list:
                logger.info(f"No {params['action']} found in blocks {params['startblock']} to {params['endblock']}")
            else:
                logger.error(f"* Error while executing API request to Etherscan in kudos_revenue => {rs_json['message']}: {rs_json['result']}")
            return []
        records = [rec for rec in rs_json['result'] if rec['to'] == params['address']]
        logger.info(f"Total {params['action']} found in blocks {params['startblock']} to {params['endblock']}: {len(records)}")
        return records
    except Exception as e:
        logger.error(f"* Exception in kudos_revenue => {e}")


def save_incoming_tx(network, record):
    if not DigitalGoodPurchase.objects.filter(txid__iexact=record['hash']).exists():
        decimals = 18. if len(record['contractAddress']) == 0 else float(record['tokenDecimal'])
        dgp = DigitalGoodPurchase.objects.create(
            emails=[],
            tokenName='ETH' if len(record['contractAddress']) == 0 else record['tokenSymbol'],
            tokenAddress=record['contractAddress'],
            amount=(int(record['value']) / decimals) if decimals > 0 else int(record['value']),
            ip='',
            network=network,
            from_address=record['from'],
            receive_address=record['to'],
            metadata=record,
            txid=record['hash'],
            receive_txid=record['hash'],
        )
        dgp.update_tx_status()
        dgp.update_receive_tx_status()
        dgp.save()


class Command(BaseCommand):

    help = 'tracks kudos purchases'

    def add_arguments(self, parser):
        parser.add_argument('network', default='mainnet', type=str)
        parser.add_argument(
            '--account-address',
            default=settings.KUDOS_REVENUE_ACCOUNT_ADDRESS,
            type=str,
            help="Account address to track revenue"
        )
        parser.add_argument(
            '--start-block',
            default=DEFAULT_START_BLOCK,
            type=int,
            help="Start at block number"
        )
        parser.add_argument(
            '--end-block',
            default=99999999999,
            type=int,
            help="End at block number"
        )

    def handle(self, *args, **options):
        if settings.ETHERSCAN_API_KEY == '':
            logger.warning("* Environment variable ETHERSCAN_API_KEY has not been set")

        # config
        network = options['network']
        params  = {
            'module': 'account',
            'address': options['account_address'],
            'startblock': options['start_block'],
            'endblock': options['end_block'],
            'apikey': settings.ETHERSCAN_API_KEY,
            'sort': 'asc'
        }

        # Get incoming ETH transactions
        dgp_records = DigitalGoodPurchase.objects \
            .filter(receive_address__iexact=options['account_address'], tokenName__iexact='ETH') \
            .order_by('-id') \
            .values('id', 'metadata')[:1]
        
        if len(dgp_records) > 0:
            params['startblock'] = int(dgp_records[0]['metadata']['blockNumber']) + 1
            logger.info(f"ETH Tx Records were found. Continuing from block {params['startblock']}")
        
        params['action'] = 'txlist'
        records = call_etherscan_api(network, params)
        for rec in records:
            save_incoming_tx(network, rec)

        # Get incoming Token transactions
        dgp_records = DigitalGoodPurchase.objects \
            .filter(receive_address__iexact=options['account_address']) \
            .exclude(tokenName='ETH') \
            .order_by('-id') \
            .values('id', 'metadata')[:1]

        if len(dgp_records) > 0:
            params['startblock'] = int(dgp_records[0]['metadata']['blockNumber']) + 1
            logger.info(f"Token Tx Records were found. Continuing from block {params['startblock']}")

        params['action'] = 'tokentx'
        records = call_etherscan_api(network, params)
        for rec in records:
            save_incoming_tx(network, rec)
