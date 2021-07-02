import logging

from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity, txn_already_used
from economy.models import Token
from oogway import Net, validate

logger = logging.getLogger(__name__)

def find_txn_on_btc_explorer(fulfillment, network='mainnet'):
    funderAddress = fulfillment.bounty.bounty_owner_address

    token = Token.objects.filter(symbol='BTC').first()
    decimal = token.decimals if token else 8
    amount = fulfillment.payout_amount * 10 ** decimal

    payeeAddress = fulfillment.fulfiller_address

    n = Net(provider='Blockstream', network=network)
    txlist = n.txs(funderAddress)

    # validate BTC address
    is_valid = validate.is_valid_address(funderAddress)
    if is_valid == False:
        logger.error(f'error: invalid BTC address - {funderAddress}')
    else:
        if network == 'mainnet':
            blockstream_url = 'https://blockstream.info/api/tx/'
        else:
            blockstream_url = 'https://blockstream.info/testnet/api/tx/'

        if txlist != []:
            for txn in txlist:
                blockstream_response = requests.get(blockstream_url+txn).json()
                if (
                    blockstream_response['vin'][0]['prevout']['scriptpubkey_address'] == str(funderAddress) and
                    blockstream_response['vout'][0]['scriptpubkey_address'] == str(payeeAddress) and
                    float(blockstream_response['vout'][0]['value']) == float(amount) and
                    not txn_already_used(txn, 'BTC')
                ):
                    return txn
    return None


def get_btc_txn_status(txnid, network='mainnet'):
    if not txnid or txnid == "0x0":
        return None

    if network == 'mainnet':
        blockstream_url = f'https://blockstream.info/api/tx/{txnid}'
    else:
        blockstream_url = f'https://blockstream.info/testnet/api/tx/{txnid}'

    blockstream_response = requests.get(blockstream_url)

    if blockstream_response.status_code == 200:
        return True

    return None


def sync_btc_payout(fulfillment):
    if not fulfillment.payout_tx_id or fulfillment.payout_tx_id == "0x0":
        txn = find_txn_on_btc_explorer(fulfillment)
        fulfillment.payout_tx_id = txn

    if fulfillment.payout_tx_id and fulfillment.payout_tx_id != "0x0":
        txn_status = get_btc_txn_status(fulfillment.payout_tx_id)
        if txn_status:
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)
        fulfillment.save()
