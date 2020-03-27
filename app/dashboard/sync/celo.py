from django.utils import timezone

import requests
from dashboard.models import BountyFulfillment
from dashboard.utils import txn_already_used


def find_txn_on_celo_explorer(fulfillment, network='mainnet'):
    token_name = fulfillment.token_name
    if token_name != 'CELO':
        return None

    funderAddress = fulfillment.bounty.bounty_owner_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    # TODO: UPDATE URL + RESPONSE
    blockscout_url = f'https://blockscout.com/etc/{network}/api?module=account&action=txlist&address={funderAddress}'
    blockscout_response = requests.get(blockscout_url).json()
    if blockscout_response['message'] and blockscout_response['result']:
        for txn in blockscout_response['result']:
            if (
                txn['from'] == funderAddress.lower() and
                txn['to'] == payeeAddress.lower() and
                float(txn['value']) >= float(amount) and
                not txn_already_used(txn, token_name)
            ):
                return txn
    return None


def get_celo_txn_status(txnid, network='mainnet'):
    if not txnid:
        return None

    # TODO: UPDATE URL + RESPONSE
    blockscout_url = f'https://blockscout.com/etc/{network}/api?module=transaction&action=gettxinfo&txhash={txnid}'
    blockscout_response = requests.get(blockscout_url).json()

    if blockscout_response['status'] and blockscout_response['result']:

        response = {
            'blockNumber': int(blockscout_response['result']['blockNumber']),
            'confirmations': int(blockscout_response['result']['confirmations'])
        }

        if response['confirmations'] > 0:
            response['has_mined'] = True
        else:
            response['has_mined'] = False
        return response

    return None


def sync_celo_payout(fulfillment):
    network = 'alfajores' # TODO: decide where network will be obtained from
    if not fulfillment.payout_tx_id:
        txn = find_txn_on_celo_explorer(fulfillment, network)
        fulfillment.payout_tx_id = txn['hash']

    if fulfillment.payout_tx_id:
        if get_celo_txn_status(fulfillment.payout_tx_id, network).get('has_mined'):
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
        fulfillment.save()
