import json

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used
from economy.models import Token

headers = {
    'Host': 'gitcoin.co'
}

def find_txn_on_filecoin_explorer(fulfillment):
    token_name = fulfillment.token_name
    payeeAddress = fulfillment.fulfiller_address

    if token_name != 'FIL':
        return None

    url = 'https://api.filscan.io:8700/rpc/v1'

    data = {
        "id": 1,
        "jsonrpc": "2.0",
        "params": [
            {
                "address": payeeAddress,
                "offset_range": {
                    "start": 0,
                    "count": 25
                }
            }
        ],
        "method": "filscan.MessageByAddress"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data)).json()
    if (
        response and
        'result' in response and
        'data' in response['result']
    ):
        for txn in response['result']['data']:
            if (
                isValidTxn(fulfillment, txn) == 'success' and
                not txn_already_used(txn['cid'], token_name) 
            ):
                return txn
    return None


def get_filecoin_txn_status(fulfillment):

    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name

    if token_name != 'FIL':
        return None

    if not txnid or txnid == "0x0":
        return None

    url = 'https://api.filscan.io:8700/rpc/v1'

    data = {
        "id": 1,
        "jsonrpc": "2.0",
        "params": [ txnid ],
        "method": "filscan.MessageDetails"
    }

    filscan_response = requests.post(url, headers=headers, data=json.dumps(data)).json()
    if filscan_response and 'result' in filscan_response:
        txn = filscan_response['result']
        if 'exit_code' in txn:
            return 'expired'
        elif isValidTxn(fulfillment, txn):
            return 'success'

    return None


def sync_filecoin_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_filecoin_explorer(fulfillment)
        if txn:
            fulfillment.payout_tx_id = txn['cid']
            fulfillment.save()

    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_filecoin_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            fulfillment.save()
            record_payout_activity(fulfillment)
        
        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'
            fulfillment.save()


def isValidTxn(fulfillment, txn):
    funderAddress = fulfillment.bounty.bounty_owner_address

    token = Token.objects.filter(symbol='FIL').first()
    decimal = token.decimals if token else 18
    amount = fulfillment.payout_amount * 10 ** decimal

    payeeAddress = fulfillment.fulfiller_address

    if (
        txn['from'] == funderAddress.lower() and
        txn['to'] == payeeAddress.lower() and
        float(txn['value']) == float(amount) and
        txn['method_name'] == 'transfer'
    ):
        return True
    
    return False
