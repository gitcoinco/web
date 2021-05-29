import logging
import re

from django.conf import settings
from django.utils import timezone

import requests
from bs4 import BeautifulSoup
from dashboard.sync.helpers import record_payout_activity

logger = logging.getLogger(__name__)

API_KEY = settings.ETHERSCAN_API_KEY

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0. 2272.118 Safari/537.36.'}


def get_eth_txn_status(fulfillment):

    txnid = fulfillment.payout_tx_id
    network = fulfillment.bounty.network if fulfillment.bounty.network else None

    if not txnid:
        return None

    response = {
        'status': 'pending'
    }

    try:
        if network == 'mainnet':
            etherscan_url = f'https://api.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={txnid}&apikey={API_KEY}'
        else:
            etherscan_url = f'https://api-rinkeby.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={txnid}&apikey={API_KEY}'

        etherscan_response = requests.get(etherscan_url, headers=headers).json()
        result = etherscan_response['result']

        response = {
            'status': 'pending'
        }

        if result:

            if result.get('status') == '1':
                response = {
                    'status': 'done'
                }
            elif result.get('status') == '0':
                response = {
                    'status': 'expired'
                }
            else:
                replacedTxnId = getReplacedTX(txnid)
                if replacedTxnId:
                    fulfillment.payout_tx_id = replacedTxnId
                    fulfillment.save()
                    response = get_eth_txn_status(fulfillment)

    except Exception as e:
        logger.error(f'error: get_eth_txn_status - {e}')
    finally:
        return response


def sync_eth_payout(fulfillment):
    if fulfillment.payout_tx_id:
        from economy.tx import getReplacedTX
        replacement_payout_tx_id = fulfillment.payout_tx_id
        if replacement_payout_tx_id:
            fulfillment.payout_tx_id = replacement_payout_tx_id
        txn_status = get_eth_txn_status(fulfillment)
        if txn_status:
            status_description = txn_status.get('status')
            if status_description == 'done':
                fulfillment.payout_status = 'done'
                fulfillment.accepted_on = timezone.now()
                fulfillment.accepted = True
                fulfillment.save()
                record_payout_activity(fulfillment)
            elif status_description == 'expired':
                fulfillment.payout_status = 'expired'
                fulfillment.save()


def getReplacedTX(tx):
    ethurl = "https://etherscan.io/tx/"
    response = requests.get(ethurl + tx + '/', headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    p = soup.find("span", "u-label u-label--sm u-label--warning rounded")
    if not p:
        return None
    if "Replaced" in p.text:
        q = soup.find(href=re.compile("/tx/0x"))
        return q.text
    else:
        return None
