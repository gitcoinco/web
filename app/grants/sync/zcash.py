from django.utils import timezone

import requests
from grants.sync.helpers import record_contribution_activity, txn_already_used


def find_txn_on_zcash_explorer(contribution):
    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    if subscription.tenant != 'ZCASH':
        return None

    if token_symbol != 'ZEC':
        return None

    to_address = grant.zcash_payout_address
    from_address = subscription.contributor_address
    amount = subscription.amount_per_period

    url = f'https://sochain.com/api/v2/address/ZEC/{from_address}'
    response = requests.get(url).json()

    # Check contributors txn history
    if response['status'] == 'success' and response['data'] and response['data']['txs']:
        txns = response['data']['txs']
        for txn in txns:
            if txn.get('outgoing') and txn['outgoing']['outputs']:
                for output in txn['outgoing']['outputs']:
                    if (
                        output['address'] == to_address and
                        response['data']['address'] == from_address and
                        float(output['value']) == float(amount) and
                        not txn_already_used(txn['txid'], token_symbol)
                    ):
                        return txn['txid']


    url = f'https://sochain.com/api/v2/address/ZEC/{to_address}'
    response = requests.get(url).json()

    # Check funders txn history
    if response['status'] == 'success' and response['data'] and response['data']['txs']:
        txns = response['data']['txs']
        for txn in txns:
            if txn.get('incoming') and txn['incoming']['inputs']:
                for input_tx in txn['incoming']['inputs']:
                    if (
                        input_tx['address'] == from_address and
                        response['data']['address'] == to_address and
                        not txn_already_used(txn['txid'], token_symbol)
                    ):
                        return txn['txid']
    return None


def get_zcash_txn_status(txnid):
    if not txnid:
        return None

    url = f'https://sochain.com/api/v2/is_tx_confirmed/ZEC/{txnid}'

    response = requests.get(url).json()

    if (
        response['status'] == 'success' and
        response['data'] and
        response['data']['is_confirmed']
    ):
        return True

    return None


def sync_zcash_payout(contribution):
    if not contribution.tx_id:
        txn = find_txn_on_zcash_explorer(contribution)
        if txn:
            contribution.tx_id = txn

    if contribution.tx_id:
        is_sucessfull_txn = get_zcash_txn_status(contribution.tx_id)
        if is_sucessfull_txn:
            contribution.success = True
            contribution.tx_cleared = True
            record_contribution_activity(contribution)

        contribution.save()
