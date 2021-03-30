from datetime import datetime

from django.conf import settings
from django.utils import timezone

import requests
from grants.sync.helpers import is_txn_done_recently, record_contribution_activity, txn_already_used

API_KEY = settings.XINFIN_API_KEY

def find_txn_on_xinfin_explorer(contribution):

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    if subscription.tenant != 'XINFIN':
        return None

    if token_symbol not in ['XDC']:
        return None

    to_address = grant.rsk_payout_address
    from_address = subscription.contributor_address
    amount = subscription.amount_per_period

    url = f'https://xdc.network/publicAPI?module=account&action=txlist&address={from_address}&page=0&pageSize=10&apikey={API_KEY}'
    response = requests.get(url).json()

    if response['message'] and response['result']:
        for txn in response['result']:
            to_address_match = txn['to'].lower() == to_address.lower() if token_symbol == 'XDC' else True
            if (
                txn['from'].lower() == to_address.lower() and
                to_address_match and
                float(txn['value']) == float(amount * 10 ** 18) and
                not txn_already_used(txn['hash'], token_symbol)
            ):
                return txn
    return None


def get_xinfin_txn_status(contribution, network='mainnet'):
    txnid = contribution.tx_id

    if not txnid or txnid == "0x0":
        return None

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    to_address = grant.rsk_payout_address
    from_address = subscription.contributor_address
    amount = subscription.amount_per_period

    if token_symbol not in ['XDC']:
        return None


    url = f'https://explorer.xinfin.network/publicAPI?module=transaction&action=gettxdetails&txhash={txnid}&apikey={API_KEY}'
    response = requests.get(url).json()

    if response['status'] == '0':
        return 'expired'
    elif response['result']:
        txn = response['result']

        to_address_match = txn['to'].lower() == to_address.lower() if token_symbol == 'XDC' else True

        if (
            txn['from'].lower() == from_address.lower() and
            to_address_match and
            float(float(txn['value'])/ 10**18) == float(amount) and
            not txn_already_used(txn['hash'], token_symbol)
        ):
            return 'success'  

    return None


def sync_rsk_payout(contribution):

    if not contribution.tx_id or contribution.tx_id == '0x0':
        txn = find_txn_on_xinfin_explorer(contribution)
        if txn:
            contribution.tx_id = txn['hash']
            contribution.save()

    if contribution.tx_id and contribution.tx_id != '0x0':
        txn_status = get_xinfin_txn_status(contribution)

        if txn_status == 'success':
            contribution.success = True
            contribution.tx_cleared = True
            contribution.checkout_type = 'xinfin_std'
            record_contribution_activity(contribution)
            contribution.save()
        else:
            contribution.success = True
            contribution.tx_cleared = False
            contribution.save()
