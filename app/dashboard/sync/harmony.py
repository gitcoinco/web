import json

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used


def find_txn_on_harmony_explorer(fulfillment):
    token_name = fulfillment.token_name

    funderAddress = fulfillment.bounty.bounty_owner_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name != 'ONE':
        return None


    url = f'https://explorer.hmny.io:8888/address?id={payeeAddress}&pageIndex=0&pageSize=20'


    response = requests.get(url).json()
    if (
        response and
        'address' in response and
        'shardData' in response['address']
    ):
        for shard in response['address']['shardData']:

            for tx in shard['txs']:
                if (
                    tx['from'] == funderAddress.lower() and
                    tx['to'] == payeeAddress.lower() and
                    tx['value'] ==  float(amount) * 10 ** 18 and
                    not txn_already_used(tx['hash'], token_name)
                ):
                    return tx
    return None


def get_harmony_txn_status(fulfillment):

    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.funder_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name != 'ONE':
        return None

    if not txnid or txnid == "0x0":
        return None

    url = f'https://explorer.hmny.io:8888/tx?id={txnid}'


    response = requests.get(url).json()
    if (response and 'tx' in response):
        tx = response['tx']

        if 'err' in tx:
            # txn hasn't been published to chain yet
            return None

        if (
            tx['from'] == funderAddress.lower() and
            tx['to'] == payeeAddress.lower() and
            tx['value']== float(amount) * 10 ** 18 and
            not txn_already_used(tx['hash'], token_name)
        ):
            if tx['status'] == 'SUCCESS':
                return 'success'

    return None


def sync_harmony_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_harmony_explorer(fulfillment)
        if txn:
            fulfillment.payout_tx_id = txn['hash']
            fulfillment.save()

    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_harmony_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)

        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'

        fulfillment.save()
