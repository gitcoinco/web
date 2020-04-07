from dashboard.abi import erc20_abi
from bs4 import BeautifulSoup
from decimal import Decimal
from hexbytes import HexBytes
from time import sleep
from dashboard.utils import get_web3
from django.conf import settings
import requests
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
import decimal
from dashboard.utils import get_tx_status
from django.utils import timezone

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
    sleep(2)  # 2s delay to avoid getting the finger from etherscan
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
        if (transfer_event or deposit_event):
            return {
                'token_amount': human_readable_value,
                'to': '',
                'token_name': contract_symbol,
            }
    except BadFunctionCallOutput as e:
        pass
    except Exception as e:
        print(e)


def check_transaction_contract(transaction_tax):
    transaction = check_transaction(transaction_tax)
    if transaction is not None:
        token_address = check_token(transaction.to)
        if token_address is not False and not token_address == '0x0000000000000000000000000000000000000000':
            return transaction_status(transaction, transaction_tax)


def grants_transaction_validator(tx_list, token_address, network):
    token_transfer = {}
    txns = []
    for tx in tx_list:

        if not tx:
            continue

        # check for dropped and replaced txn
        status, timestamp = get_tx_status(tx, network, timezone.now())
        if status in ['pending', 'dropped', 'unknown', '']:
            new_tx = getReplacedTX(tx)
            if new_tx:
                tx = new_tx
                status, timestamp = get_tx_status(tx, network, timezone.now())

        # check for txfrs
        if status == 'success':

            # check if it was an ETH transaction
            transaction_receipt = w3.eth.getTransactionReceipt(tx)
            if (transaction_receipt != None and transaction_receipt.cumulativeGasUsed >= 2100):
                transaction_hash = transaction_receipt.transactionHash.hex()
                transaction = check_transaction(transaction_hash)
                if transaction.value > 0.001:
                    token_transfer = {
                        'to': transaction.to,
                        'token_name': 'ETH',
                        'token_address': '0x0',
                        'token_amount': Decimal(transaction.value / 10 **18),
                        }

            # check if it was an ERC20 transaction
            transfer_tx = check_transaction_contract(tx)
            if transfer_tx:
                token_transfer = transfer_tx
                token_transfer['token_address'] = token_address

        # log transaction and and any xfr
        txns.append({
            'id': tx,
            'status': status,
            })
    return {
        'transfers': token_transfer,
        'txns': txns,
    }

