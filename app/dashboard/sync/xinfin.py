import json

from django.conf import settings
from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used

API_KEY = settings.XINFIN_API_KEY

def find_txn_on_xinfin_explorer(fulfillment):
    token_name = fulfillment.token_name

    funderAddress = fulfillment.bounty.bounty_owner_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name not in ['XDC']:
        return None

    url = f'https://xdc.network/publicAPI?module=account&action=txlist&address={funderAddress}&page=0&pageSize=10&apikey={API_KEY}'
    response = requests.get(url).json()

    if response['message'] and response['result']:
        for txn in response['result']:
            to_address_match = txn['to'].lower() == payeeAddress.lower() if token_name == 'XDC' else True
            if (
                txn['from'].lower() == funderAddress.lower() and
                to_address_match and
                float(txn['value']) == float(amount * 10 ** 18) and
                not txn_already_used(txn['hash'], token_name)
            ):
                return txn
    return None


def get_xinfin_txn_status(fulfillment):

    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.bounty.bounty_owner_address
    payeeAddress = fulfillment.fulfiller_address

    amount = fulfillment.payout_amount


    if token_name not in ['XDC']:
        return None

    if not txnid or txnid == "0x0":
        return None

    url = f'https://explorer.xinfin.network/publicAPI?module=transaction&action=gettxdetails&txhash={txnid}&apikey={API_KEY}'
    response = requests.get(url).json()

    if response['status'] == '0':
        return 'expired'
    elif response['result']:
        txn = response['result']

        to_address_match = txn['to'].lower() == payeeAddress.lower() if token_name == 'XDC' else True

        if (
            txn['from'].lower() == funderAddress.lower() and
            to_address_match and
            float(float(txn['value'])/ 10**18) == float(amount) and
            not txn_already_used(txn['hash'], token_name)
        ):
            return 'success'        

    return None


def sync_xinfin_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_xinfin_explorer(fulfillment)
        if txn:
            fulfillment.payout_tx_id = txn['hash']
            fulfillment.save()

    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_xinfin_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)

        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'

        fulfillment.save()
