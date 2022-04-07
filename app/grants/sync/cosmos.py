import logging

import requests
from grants.sync.helpers import record_contribution_activity

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.cosmos.network'

def get_cosmos_txn_status(contribution):
    txnid = contribution.tx_id
    token_symbol = contribution.subscription.token_symbol

    if token_symbol != 'ATOM' or not txnid or contribution.subscription.tenant != 'COSMOS':
        return None

    to_address = contribution.subscription.grant.cosmos_payout_address
    from_address = contribution.subscription.contributor_address
    amount = contribution.subscription.amount_per_period

    try:
        response = requests.get(f'{BASE_URL}/cosmos/tx/v1beta1/txs/{txnid}').json()

        tx_response = response.get('tx')

        if tx_response and tx_response['body']['messages'][0]['@type'] == '/cosmos.bank.v1beta1.MsgSend':
            tx_response = tx_response['body']['messages'][0]
            block_tip = requests.get(
                f'{BASE_URL}/blocks/latest'
            ).json()['block']['header']['height']
            confirmations = int(block_tip) - int(response['tx_response']['height'])

            if (
                response['tx_response']['txhash'].strip() == txnid
                and tx_response['from_address'] == from_address
                and tx_response['to_address'] == to_address
                and float([
                    token['amount'] for token in tx_response['amount'] if token['denom'] == 'uatom'
                ][0]) == float(amount)
            ):
                if response['tx_response']['code'] == 0 and confirmations > 0:
                    return 'success'
                return 'expired'

    except Exception as e:
        logger.error(f'error: get_cosmos_txn_status - {e}')

    return None


def sync_cosmos_payout(contribution):
    if contribution.tx_id and contribution.tx_id != '0x0':
        txn_status = get_cosmos_txn_status(contribution)

        if txn_status == 'success':
            contribution.success = True
            contribution.tx_cleared = True
            contribution.checkout_type = 'cosmos_std'
            record_contribution_activity(contribution)
        elif txn_status == 'expired':
            contribution.success = True
            contribution.tx_cleared = False

        contribution.save()
