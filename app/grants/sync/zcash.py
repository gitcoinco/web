from datetime import datetime

from django.utils import timezone

import requests
from grants.sync.helpers import is_txn_done_recently, record_contribution_activity, txn_already_used


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
                    if contribution.tx_id and contribution.tx_id != '0x0':
                        if txn['txid'] == contribution.tx_id:
                            if (
                                output['address'] == to_address and
                                float(output['value']) == float(amount) and
                                is_txn_done_recently(txn['time'])
                            ):
                                return txn['txid']
                    else:
                        if (
                            output['address'] == to_address and
                            response['data']['address'] == from_address and
                            float(output['value']) == float(amount) and
                            is_txn_done_recently(txn['time']) and
                            not txn_already_used(txn['txid'], token_symbol)
                        ):
                            return txn['txid']


    url = f'https://sochain.com/api/v2/address/ZEC/{to_address}'
    response = requests.get(url).json()

    # Check funders txn history
    # if response['status'] == 'success' and response['data'] and response['data']['txs']:
    #     txns = response['data']['txs']
    #     for txn in txns:
    #         if txn.get('incoming') and txn['incoming']['inputs']:
    #             for input_tx in txn['incoming']['inputs']:
    #                 if (
    #                     input_tx['address'] == from_address and
    #                     response['data']['address'] == to_address and
    #                     is_txn_done_recently(txn['time']) and
    #                     not txn_already_used(txn['txid'], token_symbol)
    #                 ):
    #                     return txn['txid']
    return None


def is_zcash_txn_successful(txnid):
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


def is_valid_zcash_txn(contribution):

    subscription = contribution.subscription
    grant = subscription.grant

    txn_id = contribution.tx_id
    to_address = grant.zcash_payout_address
    amount = subscription.amount_per_period
    token_symbol = subscription.token_symbol


    if not txn_id or txn_id == '0x0':
        return None

    url = f'https://sochain.com/api/v2/tx/ZEC/{txn_id}'

    response = requests.get(url).json()

    if (
        response['status'] == 'success' and
        response['data'] and
        response['data']['outputs']
    ):
        for txn in response['data']['outputs']:
            if (
                txn['address'] == to_address and
                float(txn['value']) == float(amount) and
                is_txn_done_recently(response['data']['time']) and
                not txn_already_used(txn_id, token_symbol)
            ):
                return True

    return None


def sync_zcash_payout(contribution):
    is_successfull_txn = False

    if not contribution.tx_id or contribution.tx_id == '0x0':
        # user entered t-addr.
        txn = find_txn_on_zcash_explorer(contribution)
        if txn:
            contribution.tx_id = txn
            contribution.save()
            is_successfull_txn = is_zcash_txn_successful(contribution.tx_id)
    else:
        # user entered txn-id or txn-id picked up by cron.
        is_successfull_txn = is_valid_zcash_txn(contribution)

    if is_successfull_txn:
        contribution.success = True
        contribution.tx_cleared = True
        contribution.checkout_type = 'zcash_std'
        record_contribution_activity(contribution)
        contribution.save()
