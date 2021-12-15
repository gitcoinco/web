from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used

BASE_URL = 'https://api.tzkt.io/v1'


def find_txn_on_tezos_explorer(fulfillment):
    token_name = fulfillment.token_name
    funderAddress = fulfillment.funder_address
    payeeAddress = fulfillment.fulfiller_address
    amount = fulfillment.payout_amount
    txnid = fulfillment.payout_txid

    if token_name != 'XTZ':
        return None

    url = f'{BASE_URL}/accounts/{funderAddress}'

    response = requests.get(url).json()

    if response:
        for txn in response['operations']:
            if (
                txn['type'] == 'transaction'
                and txn['hash'].strip() == txnid
                and txn['sender']['address'] == funderAddress
                and txn['target']['address'] == payeeAddress
                and txn['amount'] == float(amount) * 10 ** 6
                and not txn_already_used(txn['hash'], token_name)
            ):
                return txn
    return None


def get_tezos_txn_status(fulfillment):
    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.funder_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name != 'XTZ' or not txnid:
        return None

    tx_response = requests.get(f'{BASE_URL}/operations/{txnid}').json()

    # a valid response will return a list whereas an invalid response will return a dict
    if tx_response and isinstance(tx_response, list) and len(tx_response) > 0:
        tx_response = tx_response[0]
        block_tip = requests.get(f'{BASE_URL}/head').json()['level']
        confirmations = block_tip - tx_response['level']
        if (
            tx_response['type'] == 'transaction'
            and tx_response['hash'].strip() == txnid
            and tx_response['sender']['address'] == funderAddress
            and tx_response['target']['address'] == payeeAddress
            and tx_response['amount'] == float(amount) * 10 ** 6
        ):
            if tx_response['status'] == 'applied' and confirmations > 0:
                return 'success'
            return 'expired'

    return None


def sync_tezos_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_tezos_explorer(fulfillment)
        if txn:
            fulfillment.payout_tx_id = txn['hash']
            fulfillment.save()

    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_tezos_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)
        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'

        fulfillment.save()
