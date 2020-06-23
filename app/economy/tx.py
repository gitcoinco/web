import decimal
import os
import time
from decimal import Decimal
from time import sleep

from django.conf import settings
from django.utils import timezone

import requests
from bs4 import BeautifulSoup
from dashboard.abi import erc20_abi
from dashboard.utils import get_tx_status, get_web3
from hexbytes import HexBytes
from web3 import HTTPProvider, Web3
from web3.exceptions import BadFunctionCallOutput


def maybeprint(_str, _str2=None, _str3=None):
    pass
    #print(_str)

## web3 Exceptions
class TransactionNotFound(Exception):
    """
    Raised when a tx hash used to lookup a tx in a jsonrpc call cannot be found.
    """
    pass

# scrapper settings
ethurl = "https://etherscan.io/tx/"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}

 
# ERC20 / ERC721 tokens
# Transfer(address,address,uint256)
# Deposit(address, uint256)
# Approval(address,address, uint256)
SEARCH_METHOD_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
SEARCH_METHOD_DEPOSIT = '0xaef05ca429cf234724843763035496132d10808feeac94ee79441c83b6dd519a'
SEARCH_METHOD_APPROVAL = '0x7c3bc83eb61feb549a19180bb8de62c55c110922b2a80e511547cf8deda5b25a'

PROVIDER = "wss://mainnet.infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
w3 = Web3(Web3.WebsocketProvider(PROVIDER))
check_transaction = lambda txid: w3.eth.getTransaction(txid)
check_amount = lambda amount: int(amount[75:], 16) if len(amount) == 138 else print (f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_transaction} txid: {transaction_tax[:10]} -> status: 0 False - amount was off by 0.001 {bcolors.ENDC}")
check_token = lambda token_address: len(token_address) == 42
check_contract = lambda token_address, abi : w3.eth.contract(token_address, abi=abi)
check_event_transfer =  lambda contract_address, search, txid : w3.eth.filter({ "address": contract_address, "topics": [search, txid]})
get_decimals = lambda contract : int(contract.functions.decimals().call())


# scrapes etherscan to get the replaced tx
def getReplacedTX(tx):
    response = requests.get(ethurl + tx, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    # look for span that contains the dropped&replaced msg
    p = soup.find("span", "u-label u-label--sm u-label--warning rounded")
    if not p:
        return None
    if "Replaced" in p.text:  # check if it's a replaced tx
        # get the id for the replaced tx
        q = soup.find(href=re.compile("/tx/0x"))
        return q.text
    else:
        return None


def transaction_status(transaction, txid):
    """This function is core for check grants transaction list"""
    try:
        contract_address = transaction.to
        contract = check_contract(contract_address, erc20_abi)
        approve_event = check_event_transfer(contract.address, SEARCH_METHOD_APPROVAL, txid)
        transfer_event = check_event_transfer(contract.address, SEARCH_METHOD_TRANSFER, txid)
        deposit_event = check_event_transfer(contract.address, SEARCH_METHOD_DEPOSIT, txid)
        get_symbol = lambda contract: str(contract.functions.symbol().call())
        decimals = get_decimals(contract)
        contract_value = contract.decode_function_input(transaction.input)[1]['_value']
        contract_symbol = get_symbol(contract)
        human_readable_value = Decimal(int(contract_value)) / Decimal(10 ** decimals) if decimals else None
        transfers_web3py = get_token_recipient_senders(recipient_address, dai_address)

        if (transfer_event or deposit_event):
            return {
                'token_amount': human_readable_value,
                'to': '',
                'token_name': contract_symbol,
            }
    except BadFunctionCallOutput as e:
        pass
    except Exception as e:
        maybeprint(89, e)


def check_transaction_contract(transaction_tax):
    transaction = check_transaction(transaction_tax)
    if transaction is not None:
        token_address = check_token(transaction.to)
        if token_address is not False and not token_address == '0x0000000000000000000000000000000000000000':
            return transaction_status(transaction, transaction_tax)


def grants_transaction_validator(contribution):
    tx_list = [contribution.tx_id, contribution.split_tx_id]
    network = contribution.subscription.network

    token_transfer = {}
    txns = []
    validation = {
        'passed': False,
        'comment': 'Default'
    }
    token_originators = []

    for tx in tx_list:

        if not tx:
            continue

        # check for dropped and replaced txn
        status, timestamp = get_tx_status(tx, network, timezone.now())
        maybeprint(120, round(time.time(),2))
        if status in ['pending', 'dropped', 'unknown', '']:
            new_tx = getReplacedTX(tx)
            if new_tx:
                tx = new_tx
                status, timestamp = get_tx_status(tx, network, timezone.now())

        maybeprint(127, round(time.time(),2))
        # check for txfrs
        if status == 'success':

            # check if it was an ETH transaction
            maybeprint(132, round(time.time(),2))
            transaction_receipt = w3.eth.getTransactionReceipt(tx)
            from_address = transaction_receipt['from']
            # todo save back to the txn if needed?
            if (transaction_receipt != None and transaction_receipt.cumulativeGasUsed >= 2100):
                maybeprint(138, round(time.time(),2))
                transaction_hash = transaction_receipt.transactionHash.hex()
                transaction = check_transaction(transaction_hash)
                if transaction.value > 0.001:
                    recipient_address = Web3.toChecksumAddress(contribution.subscription.grant.admin_address)
                    transfer = get_token_originators(recipient_address, '0x0', from_address=from_address, return_what='transfers', tx_id=tx, amount=contribution.subscription.amount_per_period_minus_gas_price)
                    if transfer:
                        token_transfer = transfer
                maybeprint(148, round(time.time(),2))
                if not token_originators:

                    token_originators = get_token_originators(from_address, '0x0', from_address=None, return_what='originators')

            maybeprint(150, round(time.time(),2))
            # check if it was an ERC20 transaction
            if contribution.subscription.contributor_address and \
                contribution.subscription.grant.admin_address and \
                contribution.subscription.token_address:

                from_address = Web3.toChecksumAddress(contribution.subscription.contributor_address)
                recipient_address = Web3.toChecksumAddress(contribution.subscription.grant.admin_address)
                token_address = Web3.toChecksumAddress(contribution.subscription.token_address)

                maybeprint(160, round(time.time(),2))
                # get token transfers
                if not token_transfer:
                    transfers = get_token_originators(recipient_address, token_address, from_address=from_address, return_what='transfers', tx_id=tx, amount=contribution.subscription.amount_per_period_minus_gas_price)
                    if transfers:
                        token_transfer = transfers
                maybeprint(169, round(time.time(),2))
                if not token_originators:
                    token_originators = get_token_originators(from_address, token_address, from_address=None, return_what='originators')
                maybeprint(170, round(time.time(),2))


        # log transaction and and any xfr
        txns.append({
            'id': tx,
            'status': status,
            })

    if not token_transfer:
        validation['comment'] = "No Transfers Occured"
        validation['passed'] = False
    else:
        if token_transfer['token_name'] != contribution.subscription.token_symbol:
            validation['comment'] = f"Tokens do not match, {token_transfer['token_name']} != {contribution.subscription.token_symbol}"
            validation['passed'] = False

            from_address = Web3.toChecksumAddress(contribution.subscription.contributor_address)
            recipient_address = Web3.toChecksumAddress(contribution.subscription.grant.admin_address)
            token_address = Web3.toChecksumAddress(contribution.subscription.token_address)
            _transfers = get_token_originators(recipient_address, token_address, from_address=from_address, return_what='transfers', tx_id=tx, amount=contribution.subscription.amount_per_period_minus_gas_price)
            failsafe = _transfers['token_name'] == contribution.subscription.token_symbol
            if failsafe:
                validation['comment'] = f"Token Transfer Passed on the second try"
                validation['passed'] = True
                token_transfer = _transfers

        else:
            delta1 = Decimal(token_transfer['token_amount_decimal']) - Decimal(contribution.subscription.amount_per_period_minus_gas_price)
            delta2 = Decimal(token_transfer['token_amount_decimal']) - Decimal(contribution.subscription.amount_per_period)
            # TODO what about gitcoin transfers
            validation['passed'] = abs(delta1) <= 0.01 or abs(delta2) <= 0.01
            validation['comment'] = f"Transfer Amount is off by {round(delta1, 2)} / {round(delta2, 2)}"


    return {
        'contribution': {
            'pk': contribution.pk,
            'amount_per_period_to_gitcoin': contribution.subscription.amount_per_period_to_gitcoin,
            'amount_per_period_to_grantee': contribution.subscription.amount_per_period_minus_gas_price,
            'from': contribution.subscription.contributor_address,
            'to': contribution.subscription.grant.admin_address,
        },
        'validation': validation,
        'transfers': token_transfer,
        'originator': token_originators,
        'txns': txns,
    }


def trim_null_address(address):
    if address == '0x0000000000000000000000000000000000000000':
        return '0x0'
    else:
        return address


def get_token_recipient_senders(recipient_address, token_address):
    PROVIDER = "wss://mainnet.infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
    w3 = Web3(Web3.WebsocketProvider(PROVIDER))
    contract = w3.eth.contract(
        address=token_address,
        abi=erc20_abi,
    )

    balance = contract.functions.balanceOf(recipient_address).call()

    transfers = contract.events.Transfer.getLogs(
        fromBlock=0,
        toBlock="latest",
        argument_filters={"to": recipient_address})

    return [
        trim_null_address(transfer.args['from'])
        for transfer in transfers
    ]


auth = settings.ALETHIO_KEY
headers = {'Authorization': f'Bearer {auth}'}

def get_token_originators(to_address, token, from_address='', return_what='transfers', tx_id='', amount=None):
    address = to_address

    #is_address = requests.get('https://api.aleth.io/v1/accounts/' + address, headers=headers).status_code

    #if is_address != requests.codes.ok:
    #    raise ValueError('Address provided is not valid.')

    #is_token = requests.get(
    #    'https://api.aleth.io/v1/tokens/' + (token),
    #    headers=headers
    #).status_code

    #if is_token != requests.codes.ok and token != '0x0':
    #    raise ValueError('Token provided is not valid.')

    #balance = 0
    #try:
        #url = 'https://api.aleth.io/v1/token-balances?filter[account]=' + address + '&filter[token]=' + token
        #balance = requests.get(url, headers=headers).json()['data'][0]['attributes']['balance']
    #    pass
        #if balance == 0:
        #    raise ValueError('No balance of token at address provided.')
    #except Exception as e:
    #    maybeprint(250, e)

    endpoint = 'token-transfers' if token != '0x0' else 'ether-transfers'
    url = f'https://api.aleth.io/v1/{endpoint}?filter[to]=' + address + '&filter[token]=' + token + '&page%5Blimit%5D=100'
    if token == '0x0':
        url = f'https://api.aleth.io/v1/{endpoint}?filter[account]=' + address + '&page%5Blimit%5D=100'
    if from_address:
        url += '&filter[from]=' + from_address

    transfers = requests.get(
        url,
        headers=headers
    ).json()
    if transfers.get('message') == 'API rate limit exceeded. Please upgrade your account.':
        raise Exception("RATE LIMIT EXCEEDED")
    # TODO - pull more than one page in case there are many transfers.

    if return_what == 'transfers':
        for transfer in transfers.get('data', {}):
            this_is_the_one = tx_id and tx_id.lower() in str(transfer).lower()
            _decimals = transfer.get('attributes', {}).get('decimals', 18)
            _symbol = transfer.get('attributes', {}).get('symbol', 'ETH')
            _value = transfer.get('attributes', {}).get('value', 0)
            _value_decimal = Decimal(int(_value) / 10 ** _decimals)
            if amount:
                delta = abs(float(abs(_value_decimal)) - float(abs(amount)))
                this_is_the_one = delta < 0.001
            if this_is_the_one:
                if transfer.get('type') in ['TokenTransfer', 'EtherTransfer']:
                    return {
                            'token_amount_decimal': _value_decimal,
                            'token_name': _symbol,
                            'to': address,
                            'token_address': token,
                            'token_amount_int': int(transfer['attributes']['value']),
                            'decimals': _decimals,
                    }
        return None

    # TokenTransfer events, value field
    try:
        originators = []
        xfrs = transfers.get('data', {})
        for tx in xfrs:
            if tx.get('type') == 'TokenTransfer':
                response = tx['relationships']['from']['data']['id']
                # hack to save time
                if response != to_address:
                    return [response]
                #originators.append(response)
            value = int(tx.get('attributes', {}).get('value', 0))
            if tx.get('type') == 'EtherTransfer' and value > 0 and token == '0x0':
                response = tx['relationships']['from']['data']['id']
                if response != to_address:
                    # hack to save time
                    return [response]
                    originators.append(response)

        return list(set(originators))
    except Exception as e:
        maybeprint('284', e)
        return []
