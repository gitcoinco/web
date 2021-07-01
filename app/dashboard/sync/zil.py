import json

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used
from economy.models import Token

headers = {
    "X-APIKEY" : settings.VIEW_BLOCK_API_KEY
}

def find_txn_on_zil_explorer(fulfillment, network='mainnet'):
    token_name = fulfillment.token_name
    if token_name != 'ZIL':
        return None

    funderAddress = fulfillment.bounty.bounty_owner_address

    token = Token.objects.filter(symbol=token_name).first()
    decimal = token.decimals
    amount = fulfillment.payout_amount * 10 ** decimal

    payeeAddress = fulfillment.fulfiller_address

    url = f'https://api.viewblock.io/v1/zilliqa/addresses/{funderAddress}/txs?network={network}'
    response = requests.get(url, headers=headers).json()
    if len(response):
        for txn in response:
            if (
                txn['from'] == funderAddress.lower() and
                txn['to'] == payeeAddress.lower() and
                txn['direction'] == 'out' and
                float(txn['value']) == float(amount) and
                not txn_already_used(txn['hash'], token_name)
            ):
                return txn
    return None


def get_zil_txn_status(txnid, network='mainnet'):
    if not txnid or txnid == "0x0":
        return None

    url = f'https://api.viewblock.io/v1/zilliqa/txs/{txnid}?network={network}'
    view_block_response = requests.get(url, headers=headers).json()
    if view_block_response:

        response = {
            'blockHeight': int(view_block_response['blockHeight']),
            'receiptSuccess': view_block_response['receiptSuccess']
        }

        if response['receiptSuccess']:
            response['has_mined'] = True
        else:
            response['has_mined'] = False
        return response

    return None


def sync_zil_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_zil_explorer(fulfillment)
        if txn:
            fulfillment.payout_tx_id = txn['hash']
            fulfillment.save()

    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_zil_txn_status(fulfillment.payout_tx_id)
        if txn_status and txn_status.get('has_mined'):
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            fulfillment.save()
            record_payout_activity(fulfillment)
