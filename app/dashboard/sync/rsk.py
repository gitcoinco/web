import json

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used


def find_txn_on_rsk_explorer(fulfillment):
    token_name = fulfillment.token_name

    funderAddress = fulfillment.bounty.bounty_owner_address
    # amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name not in ['RBTC', 'RDOC', 'DOC', 'RIF', 'SOV']:
        return None

    url = f'https://blockscout.com/rsk/mainnet/api?module=account&action=txlist&address={funderAddress}'

    response = requests.get(url).json()

    if response['message'] and response['result']:
        for txn in response['result']:
            to_address_match = txn['to'] == payeeAddress.lower() if token_name == 'RBTC' else True

            if (
                txn['from'] == funderAddress.lower() and
                to_address_match and
                # float(txn['value']) == float(amount * 10 ** 18) and
                not txn_already_used(txn['hash'], token_name)
            ):
                return txn
    return None


def get_rsk_txn_status(fulfillment):

    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.bounty.bounty_owner_address
    payeeAddress = fulfillment.fulfiller_address

    # amount = fulfillment.payout_amount

    if token_name not in ['RBTC', 'RDOC', 'DOC', 'RIF', 'SOV']:
        return None

    if not txnid or txnid == "0x0":
        return None

    url = f'https://blockscout.com/rsk/mainnet/api?module=transaction&action=gettxinfo&txhash={txnid}'

    response = requests.get(url).json()
   
    if response['status'] and response['result']:
        txn = response['result']

        to_address_match = txn['to'] == payeeAddress.lower() if token_name == 'RBTC' else True

        if (
            txn['from'] == funderAddress.lower() and
            to_address_match and
            # float(txn['value']) == float(amount * 10 ** 18) and
            not txn_already_used(txn['hash'], token_name) and
            int(txn['confirmations']) > 0
        ):
            if txn['success']:
                return 'success'
            return 'expired'

    return None


def sync_rsk_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_rsk_explorer(fulfillment)
        if txn:
            fulfillment.payout_tx_id = txn['hash']
            fulfillment.save()

    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_rsk_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)

        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'

        fulfillment.save()
