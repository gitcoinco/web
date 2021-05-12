import json

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used

API_KEY = settings.ALGORAND_API_KEY


def get_algorand_txn_status(fulfillment):
    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.bounty.bounty_owner_address
    payeeAddress = fulfillment.fulfiller_address
    amount = fulfillment.payout_amount

    url = f'https://api.algoexplorer.io/v2/transactions/pending/{txnid}?format=json'
    response = requests.get(url).json()
    if response:

        if response.get('confirmed-round') and response.get('txn') and response.get('txn').get('txn'):
            txn = response["txn"]['txn']
            if not response["pool-error"] == "":
                return None

            # asset / algo token
            rcv = txn['rcv'] if txn.get('rcv') else txn['arcv']
            amt = txn['amt'] if txn.get('amt') else txn['aamt']

            if (
                txn['snd'].lower() == funderAddress.lower() and
                rcv.lower() == payeeAddress.lower() and
                float(float(amt)/ 10**6) == float(amount) and
                not txn_already_used(txnid, token_name)
            ):
                return 'success'    
        
        elif response.get('message') and API_KEY != '':
            # txn is too old and cannot be found on algoexplorer
            return get_algorand_txn_status_paid_explorer(fulfillment)
        

def get_algorand_txn_status_paid_explorer(fulfillment):
    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.bounty.bounty_owner_address
    payeeAddress = fulfillment.fulfiller_address
    amount = fulfillment.payout_amount

    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    url = f'https://mainnet-algorand.api.purestake.io/idx2/v2/transactions/{txnid}'
    response = requests.get(url=url, headers=headers).json()
    
    if response:
        if response.get("current-round") and response.get("transaction"):
            txn = response["transaction"]

            # asset / algo token
            payment_txn = txn['payment-transaction'] if txn.get('payment-transaction') else txn['asset-transfer-transaction']

            if (
                txn['confirmed-round'] > 0 and
                txn['sender'].lower() == funderAddress.lower() and
                payment_txn['receiver'].lower() == payeeAddress.lower() and
                float(float(payment_txn['amount'])/ 10**6) == float(amount) and
                not txn_already_used(txnid, token_name)
            ):
                return 'success'
        
    return None


def sync_algorand_payout(fulfillment):
    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_algorand_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)

        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'

        fulfillment.save()
