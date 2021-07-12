import requests
from grants.sync.helpers import record_contribution_activity, txn_already_used


def find_txn_on_rsk_explorer(contribution):

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    if subscription.tenant != 'RSK':
        return None

    if token_symbol not in ['RBTC', 'RDOC', 'DOC', 'RIF', 'SOV']:
        return None

    to_address = grant.rsk_payout_address
    from_address = subscription.contributor_address
    # amount = subscription.amount_per_period

    url = f'https://blockscout.com/rsk/mainnet/api?module=account&action=txlist&address={to_address}'
    response = requests.get(url).json()
    if (
        response and
        response['message'] and
        response['result']
    ):

        for txn in response['result']:
            to_address_match = txn['to'] == to_address.lower() if token_symbol == 'RBTC' else True

            if (
                txn['from'] == from_address.lower() and
                to_address_match and
                # float(txn['value']) == float(amount * 10 ** 18) and
                not txn_already_used(txn['hash'], token_symbol)
            ):
                return txn
    return None


def get_rsk_txn_status(contribution, network='mainnet'):
    txnid = contribution.tx_id

    if not txnid or txnid == "0x0":
        return None

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    to_address = grant.rsk_payout_address
    from_address = subscription.contributor_address
    # amount = subscription.amount_per_period

    if token_symbol not in ['RBTC', 'RDOC', 'DOC', 'RIF', 'SOV']:
        return None


    url = f'https://blockscout.com/rsk/mainnet/api?module=transaction&action=gettxinfo&txhash={txnid}'

    response = requests.get(url).json()

    if response['status'] and response['result']:
        txn = response['result']

        to_address_match = txn['to'] == to_address.lower() if token_symbol == 'RBTC' else True

        if (
            txn['from'] == from_address.lower() and
            to_address_match and
            # float(txn['value']) == float(amount * 10 ** 18) and
            not txn_already_used(txn['hash'], token_symbol) and
            int(txn['confirmations']) > 0
        ):
            if txn['success']:
                return 'success'
            return 'expired'

    return None


def sync_rsk_payout(contribution):

    if not contribution.tx_id or contribution.tx_id == '0x0':
        txn = find_txn_on_rsk_explorer(contribution)
        if txn:
            contribution.tx_id = txn['hash']
            contribution.save()

    if contribution.tx_id and contribution.tx_id != '0x0':
        txn_status = get_rsk_txn_status(contribution)

        if txn_status == 'success':
            contribution.success = True
            contribution.tx_cleared = True
            contribution.checkout_type = 'rsk_std'
            record_contribution_activity(contribution)
            contribution.save()
        else:
            contribution.success = True
            contribution.tx_cleared = False
            contribution.save()
