
from django.conf import settings
import time

import requests
from grants.sync.helpers import is_txn_done_recently, record_contribution_activity, txn_already_used

headers = {
    "X-APIKEY" : settings.VIEW_BLOCK_API_KEY
}

DECIMALS = 12

def find_txn_on_zil_explorer(contribution):

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    if subscription.tenant != 'ZIL':
        return None

    if token_symbol != 'ZIL':
        return None

    to_address = grant.zil_payout_address
    from_address = subscription.contributor_address
    amount = subscription.amount_per_period

    url = f'https://api.viewblock.io/v1/zilliqa/addresses/{to_address}/txs?network=mainnet'
    response = requests.get(url, headers=headers).json()

    if len(response):
        for txn in response:
            if (
                txn['from'] == from_address.lower() and
                txn['to'] == to_address.lower() and
                txn['direction'] == 'in' and
                float(txn['value']) / 10 ** DECIMALS == float(amount) and
                is_txn_done_recently(txn['timestamp']/1000) and
                not txn_already_used(txn['hash'], token_symbol)
            ):
                return txn['hash']
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


def sync_zil_payout(contribution):
    time.sleep(0.5) # to avoid rate limit

    if not contribution.tx_id or contribution.tx_id == '0x0':
        txn = find_txn_on_zil_explorer(contribution)
        if txn:
            contribution.tx_id = txn
            contribution.save()
            
    if contribution.tx_id and contribution.tx_id != '0x0':
        txn_status = get_zil_txn_status(contribution.tx_id)

        if txn_status and txn_status.get('has_mined'):
            contribution.success = True
            contribution.tx_cleared = True
            contribution.checkout_type = 'zil_std'
            record_contribution_activity(contribution)
            contribution.save()
