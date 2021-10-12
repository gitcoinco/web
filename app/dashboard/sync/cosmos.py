from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used

BASE_URL = 'https://lcd-cosmoshub.keplr.app'


def get_cosmos_txn_status(fulfillment):
    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.funder_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name != 'ATOM' or not txnid:
        return None

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
            and tx_response['from_address'] == funderAddress
            and tx_response['to_address'] == payeeAddress
            and float([
                token['amount'] for token in tx_response['amount'] if token['denom'] == 'uatom'
            ][0]) == float(amount) * 10 ** 6
        ):
            if confirmations > 0:
                return 'success'
            return 'expired'

    return None


def sync_cosmos_payout(fulfillment):
    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_cosmos_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)
        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'

        fulfillment.save()
