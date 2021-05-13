from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity

BASE_URL = 'https://siastats.info:3500/navigator-api'


def find_txn_on_sia_explorer(fulfillment):
    token_name = fulfillment.token_name

    funderAddress = fulfillment.bounty.bounty_owner_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name != 'SC':
        return None

    url = f'{BASE_URL}/hash/{funderAddress}'

    response = requests.get(url).json()

    last100_txns = response[1]['last100Transactions']

    if response and response[0]['Type'] == 'address' and last100_txns:
        for txn in last100_txns:
            if (
                txn['TxType'] == 'ScTx'
                and txn['ScChange'] < 0
                and abs(txn['ScChange']) / 10 ** 24 == amount
                and not txn_already_used(txn['MasterHash'], token_name)
            ):
                return txn
    return None


def get_sia_txn_status(txnid, network='mainnet'):
    if not txnid:
        return None
    
    tx_url = f'{BASE_URL}/hash/{txnid}'
    stats_url = f'{BASE_URL}/status'

    tx_response = requests.get(tx_url).json()

    if tx_response:
        last_block = requests.get(stats_url).json()[0]['lastblock'] # or consensusblock ?

        confirmations = last_block - tx_response[1]['Height']

        if (
            tx_response[0]['Type'] == 'ScTx'
            and tx_response[0]['MasterHash'] == txnid
            and confirmations > 0
        ):
            return True
        else:
            return False


def sync_sia_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_sia_explorer(fulfillment)
        if txn:
            fulfillment.payout_tx_id = txn['MasterHash']
            fulfillment.save()
            
    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_sia_txn_status(fulfillment.payout_tx_id)
        if txn_status:
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)
        fulfillment.save()
