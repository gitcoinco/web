from django.conf import settings

import requests
from grants.sync.helpers import record_contribution_activity, txn_already_used

API_KEY = settings.ALGORAND_API_KEY


def get_algorand_txn_status_paid_explorer(contribution):
    txnid = contribution.tx_id

    if not txnid or txnid == "0x0":
        return None
    
    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol
    amount = subscription.amount_per_period

    to_address = grant.algorand_payout_address
    from_address = subscription.contributor_address

    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    url = f'https://mainnet-algorand.api.purestake.io/idx2/v2/transactions/{txnid}'
    response = requests.get(url=url, headers=headers).json()
    
    if response:
        if response.get("current-round") and response.get("transaction"):
            txn = response["transaction"]

            # asset / algo token
            payment_txn = txn['payment-transaction'] if txn.get('payment-transaction') else txn['asset-transfer-transaction']

            if (
                txn['confirmed-round'] > 0 and
                txn['sender'].lower() == from_address.lower() and
                payment_txn['receiver'].lower() == to_address.lower() and
                float(float(payment_txn['amount'])/ 10**6) == float(amount) and
                not txn_already_used(txnid, token_symbol)
            ):
                return 'success'
        
    return None


def get_algorand_txn_status(contribution):
    txnid = contribution.tx_id

    if not txnid or txnid == "0x0":
        return None

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol
    amount = subscription.amount_per_period

    to_address = grant.algorand_payout_address
    from_address = subscription.contributor_address

    url = f'https://api.algoexplorer.io/v2/transactions/pending/{txnid}?format=json'

    response = requests.get(url).json()

    if response.get('confirmed-round') and response.get('txn') and response.get('txn').get('txn'):
        txn = response["txn"]['txn']
        if not response["pool-error"] == "":
            return None

        # asset / algo token
        rcv = txn['rcv'] if txn.get('rcv') else txn['arcv']
        amt = txn['amt'] if txn.get('amt') else txn['aamt']

        if (
            txn['snd'].lower() == from_address.lower() and
            rcv.lower() == to_address.lower() and
            float(float(amt)/ 10**6) == float(amount) and
            not txn_already_used(txnid, token_symbol)
        ):
            return 'success'    
    
    elif response.get('message') and API_KEY != '':
        # txn is too old and cannot be found on algoexplorer
        return get_algorand_txn_status_paid_explorer(contribution)

    return None


def sync_algorand_payout(contribution):

    if contribution.tx_id and contribution.tx_id != '0x0':
        txn_status = get_algorand_txn_status(contribution)

        if txn_status == 'success':
            contribution.success = True
            contribution.tx_cleared = True
            contribution.checkout_type = 'alogrand_std'
            record_contribution_activity(contribution)
            contribution.save()
        else:
            contribution.success = True
            contribution.tx_cleared = False
            contribution.save()
