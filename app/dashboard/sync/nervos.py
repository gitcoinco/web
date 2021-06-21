from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity

HEADERS = {
    'Content-Type': 'application/vnd.api+json',
    'Accept': 'application/vnd.api+json'
}


def get_nervos_txn_status(txnid, network='mainnet'):
    if not txnid:
        return None

    if network == 'mainnet':
        base_url = 'https://api.explorer.nervos.org/api/v1'
    else:
        base_url = 'https://api.explorer.nervos.org/testnet/api/v1'
    
    explorer_url = f'{base_url}/transactions/{txnid}'
    tip_block_number_url = f'{base_url}/statistics/tip_block_number'

    tx_response = requests.get(explorer_url, headers=HEADERS)

    if tx_response.status_code == 200:
        tx_data = tx_response.json()['data']['attributes']
        tip_block_number = requests.get(
            tip_block_number_url, headers=HEADERS
        ).json()['data']['attributes']['tip_block_number']
        confirmations = tip_block_number - int(tx_data['block_number'])

        if confirmations > 0 and tx_data['tx_status'] == 'committed':
            return True
        else:
            return False


def sync_nervos_payout(fulfillment):
   if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_nervos_txn_status(fulfillment.payout_tx_id)
        if txn_status:
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)
        fulfillment.save()
