import requests
from grants.sync.helpers import record_contribution_activity


def get_binance_txn_status(contribution):
    txnid = contribution.tx_id

    if not txnid or txnid == "0x0":
        return None

    response = { 'status': 'pending' }

    try:
        binance_url = f'https://bsc-dataseed.binance.org'

        data = {
            'id': 0,
            'jsonrpc': '2.0',
            'method': 'eth_getTransactionReceipt',
            'params': [ txnid ]
        }

        headers = {
            'Host': 'gitcoin.co'
        }

        binance_response = requests.post(binance_url, json=data).json()

        result = binance_response['result']

        response = { 'status': 'pending' }

        if result:
            tx_status = int(result.get('status'), 16) # convert hex to decimal

            if tx_status == 1:
                response = { 'status': 'done' }
            elif tx_status == 0:
                response = { 'status': 'expired' }

    except Exception as e:
        logger.error(f'error: get_binance_txn_status - {e}')

    finally:
        return response


def sync_binance_payout(contribution):
    if contribution.tx_id or contribution.tx_id == "0x0":
        txn_status = get_binance_txn_status(contribution)

        if txn_status:
            status_description = txn_status.get('status')

            if status_description == 'done':
                contribution.success = True
                contribution.tx_cleared = True
                contribution.checkout_type = 'binance_std'
                record_contribution_activity(contribution)
                contribution.save()
            elif status_description == 'expired':
                contribution.success = True
                contribution.tx_cleared = False
                contribution.save()
