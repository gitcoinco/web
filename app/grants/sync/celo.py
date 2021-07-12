import requests
from grants.sync.helpers import is_txn_done_recently, record_contribution_activity, txn_already_used


def find_txn_on_celo_explorer(contribution):

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    if subscription.tenant != 'CELO':
        return None

    if token_symbol != 'cUSD' and token_symbol != 'CELO':
        return None

    to_address = grant.celo_payout_address
    from_address = subscription.contributor_address
    amount = subscription.amount_per_period

    blockscout_url = f'https://explorer.celo.org/api?module=account&action=tokentx&address={to_address}'
    blockscout_response = requests.get(blockscout_url).json()

    if blockscout_response['message'] and blockscout_response['result']:
        for txn in blockscout_response['result']:
            if (
                txn['from'] == from_address.lower() and
                txn['to'] == to_address.lower() and
                int(txn['value']) / 10 ** int(txn['tokenDecimal']) == amount and
                is_txn_done_recently(txn['timeStamp']) and
                not txn_already_used(txn['hash'], token_symbol)
            ):
                return txn['hash']
    return None


def get_celo_txn_status(txnid):
    if not txnid:
        return None

    blockscout_url = f'https://explorer.celo.org/api?module=transaction&action=gettxinfo&txhash={txnid}'

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



def sync_celo_payout(contribution):
    is_successfull_txn = False

    if not contribution.tx_id or contribution.tx_id == '0x0':
        txn = find_txn_on_celo_explorer(contribution)
        if txn:
            contribution.tx_id = txn
            contribution.save()
            
    if contribution.tx_id and contribution.tx_id != '0x0':
        is_successfull_txn = get_celo_txn_status(contribution.tx_id)

        if is_successfull_txn:
            contribution.success = True
            contribution.tx_cleared = True
            contribution.checkout_type = 'celo_std'
            record_contribution_activity(contribution)
            contribution.save()
