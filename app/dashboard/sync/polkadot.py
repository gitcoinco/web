import json
import logging

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity

logger = logging.getLogger(__name__)

def get_polkadot_txn_status(txnid, token_name):
    if not txnid:
        return None

    try:
        response = { 'status': 'pending' }

        # subscan_url = f'https://polkadot.subscan.io/api/open/extrinsic'
        # payload = { "hash": txnid }
        # headers = { 'Content-Type': 'application/json'}
        # subscan_response = requests.post(subscan_url, headers=headers, data=json.dumps(payload)).json()

        # if subscan_response:
        #     status = subscan_response.get('data').get('extrinsic').get('success')

        if token_name == 'DOT':
            polkascan_url = f'https://explorer-32.polkascan.io/api/v1/polkadot/extrinsic/{txnid}'
        elif token_name == 'KSM':
            polkascan_url = f'https://explorer-32.polkascan.io/api/v1/kusama/extrinsic/{txnid}'

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0. 2272.118 Safari/537.36.'}
        polkascan_response = requests.get(polkascan_url, headers=headers).json()

        if polkascan_response:
            status = polkascan_response.get('data').get('attributes')

            if status.get('success') == 1:
                response = { 'status': 'done'}
            elif status.get('error') == 1:
                response = { 'status': 'expired' }

    except Exception as e:
        logger.error(f'error: get_polkadot_txn_status - {e}')
    finally:
        return response


def sync_polkadot_payout(fulfillment):
    if fulfillment.payout_tx_id:
        txn_status = get_polkadot_txn_status(fulfillment.payout_tx_id, fulfillment.token_name)
        if txn_status:
            status_description = txn_status.get('status')
            if status_description == 'done':
                fulfillment.payout_status = 'done'
                fulfillment.accepted_on = timezone.now()
                fulfillment.accepted = True
                fulfillment.save()
                record_payout_activity(fulfillment)
            elif status_description == 'expired':
                fulfillment.payout_status = 'expired'
                fulfillment.save()
