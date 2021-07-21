import logging

from django.utils import timezone

import requests
from dashboard.sync.helpers import record_payout_activity

logger = logging.getLogger(__name__)


def get_casper_txn_status(fulfillment):
    txnid = fulfillment.payout_tx_id
    token_name = fulfillment.token_name
    funderAddress = fulfillment.funder_address
    amount = fulfillment.payout_amount
    payeeAddress = fulfillment.fulfiller_address

    if token_name != 'CSPR' or not txnid:
        return None

    try:
        data = {
            'id': 0,
            'jsonrpc': '2.0',
            'method': 'info_get_deploy',
            'params': [ txnid ]
        }

        casper_response = requests.post('http://3.142.224.108:7777/rpc', json=data).json()

        result = casper_response['result']

        if result:
            if (
                result["deploy"]["hash"] == txnid
                and result["deploy"]["header"]["account"] == funderAddress
                and float([
                    x for x in result["deploy"]["session"]["Transfer"]["args"] if x[0] == 'amount'
                ][0][1]['parsed']) == float(amount) * 10 ** 9
            ):
                if result["execution_results"][0]["result"].get("Success", False) != False:
                    return 'success'
                return 'expired'

    except Exception as e:
        logger.error(f'error: get_casper_txn_status - {e}')

    return None


def sync_casper_payout(fulfillment):
    if fulfillment.payout_tx_id:
        txn_status = get_casper_txn_status(fulfillment)

        if txn_status == 'success':
            fulfillment.payout_status = 'done'
            fulfillment.accepted_on = timezone.now()
            fulfillment.accepted = True
            record_payout_activity(fulfillment)
        elif txn_status == 'expired':
            fulfillment.payout_status = 'expired'
        
        fulfillment.save()
