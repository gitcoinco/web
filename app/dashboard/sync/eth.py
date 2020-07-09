import logging

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity

logger = logging.getLogger(__name__)

API_KEY = settings.ETHERSCAN_API_KEY

def get_eth_txn_status(txnid, network='mainnet'):
    if not txnid:
        return None

    response = {
        'status': 'pending'
    }

    try:
        if network == 'mainnet':
            etherscan_url = f'https://api.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={txnid}&apikey={API_KEY}'
        else:
            etherscan_url = f'https://api-rinkeby.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={txnid}&apikey={API_KEY}'

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0. 2272.118 Safari/537.36.'}
        etherscan_response = requests.get(etherscan_url, headers=headers).json()
        result = etherscan_response['result']

        response = {
            'status': 'pending'
        }

        if result:

            if result.get('status') == '1':
                response = {
                    'status': 'done'
                }
            elif result.get('status') == '0':
                response = {
                    'status': 'expired'
                }

    except Exception as e:
        logger.error(f'error: get_eth_txn_status - {e}')
    finally:
        return response


def sync_eth_payout(fulfillment):
    if fulfillment.payout_tx_id:
        txn_status = get_eth_txn_status(fulfillment.payout_tx_id, fulfillment.bounty.network)
        if txn_status:
            if txn_status.get('status') == 'done':
                fulfillment.payout_status = 'done'
                fulfillment.accepted_on = timezone.now()
                fulfillment.accepted = True
                record_payout_activity(fulfillment)
            elif txn_status.get('status') == 'expired':
                fulfillment.payout_status = 'expired'

        fulfillment.save()
