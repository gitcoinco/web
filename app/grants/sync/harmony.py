import requests
from grants.sync.helpers import record_contribution_activity, txn_already_used


def find_txn_on_harmony_explorer(contribution):

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    if subscription.tenant != 'HARMONY':
        return None

    if token_symbol != 'ONE':
        return None

    to_address = grant.harmony_payout_address
    from_address = subscription.contributor_address
    amount = subscription.amount_per_period

    url = f'https://explorer.hmny.io:8888/address?id={to_address}&pageIndex=0&pageSize=20'

    response = requests.get(url).json()
    if (
        response and
        'address' in response and
        'shardData' in response['address']
    ):
        for shard in response['address']['shardData']:

            for tx in shard['txs']:
                if (
                    tx['from'] == from_address.lower() and
                    tx['to'] == to_address.lower() and
                    tx['value'] ==  float(amount) * 10 ** 18 and
                    not txn_already_used(tx['hash'], token_symbol)
                ):
                    return tx
    return None


def get_harmony_txn_status(contribution, network='mainnet'):
    txnid = contribution.tx_id

    if not txnid or txnid == "0x0":
        return None

    subscription = contribution.subscription
    grant = subscription.grant
    token_symbol = subscription.token_symbol

    to_address = grant.harmony_payout_address
    from_address = subscription.contributor_address
    amount = subscription.amount_per_period

    url = f'https://explorer.hmny.io:8888/tx?id={txnid}'


    response = requests.get(url).json()
    if (response and 'tx' in response):
        tx = response['tx']

        if 'err' in tx:
            # txn hasn't been published to chain yet
            return None

        if (
            tx['from'] == from_address.lower() and
            tx['to'] == to_address.lower() and
            tx['value']== float(amount) * 10 ** 18 and
            not txn_already_used(tx['hash'], token_symbol)
        ):
            if tx['status'] == 'SUCCESS':
                return 'success'

    return None


def sync_harmony_payout(contribution):

    if not contribution.tx_id or contribution.tx_id == '0x0':
        txn = find_txn_on_harmony_explorer(contribution)
        if txn:
            contribution.tx_id = txn['hash']
            contribution.save()
            
    if contribution.tx_id and contribution.tx_id != '0x0':
        txn_status = get_harmony_txn_status(contribution)

        if txn_status == 'success':
            contribution.success = True
            contribution.tx_cleared = True
            contribution.checkout_type = 'harmony_std'
            record_contribution_activity(contribution)
            contribution.save()
        else:
            contribution.success = True
            contribution.tx_cleared = False
            contribution.save()
