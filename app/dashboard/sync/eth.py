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
    raw_data = None
    try:
        if network == 'mainnet':
            etherscan_url = f'https://api.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={txnid}&apikey={API_KEY}'
        else:
            etherscan_url = f'https://api-rinkeby.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={txnid}&apikey={API_KEY}'

        # Make request
        etherscan_response = requests.get(etherscan_url, headers=headers)
        # Raise exception if status != 200
        etherscan_response.raise_for_status()
        # retaining raw data for the purpose of logging it in case of error
        raw_data = etherscan_response.text
        # Parse JSON response
        etherscan_response = etherscan_response.json()

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

    except requests.HTTPError as e:
        logger.error(f'HTTP error: get_eth_txn_status - {fulfillment} - {e.response.text}', exc_info=True)
    except Exception as e:
        logger.error(f'Error: get_eth_txn_status - {fulfillment} - raw data: {raw_data}', exc_info=True)
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
    try:
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
    except Exception:
        return None
