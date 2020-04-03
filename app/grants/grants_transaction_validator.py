import sys
import json
import time
import re
import requests
import pandas as pd

from bs4 import BeautifulSoup
from decimal import Decimal
from hexbytes import HexBytes
from time import sleep
from web3.auto.infura import w3

## web3 Exceptions
class TransactionNotFound(Exception):
    """
    Raised when a tx hash used to lookup a tx in a jsonrpc call cannot be found.
    """
    pass

# ERC20 / ERC721 tokens
# Transfer(address,address,uint256)
# Deposit(address, uint256)
# Approval(address,address, uint256)
SEARCH_METHOD_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
SEARCH_METHOD_DEPOSIT = '0xaef05ca429cf234724843763035496132d10808feeac94ee79441c83b6dd519a'
SEARCH_METHOD_APPROVAL = '0x7c3bc83eb61feb549a19180bb8de62c55c110922b2a80e511547cf8deda5b25a'

# ERC20 ABI
erc20_abi = json.loads('[{"constant":true,"inputs":[],"name":"mintingFinished","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_amount","type":"uint256"}],"name":"mint","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_subtractedValue","type":"uint256"}],"name":"decreaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"finishMinting","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_addedValue","type":"uint256"}],"name":"increaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"payable":false,"stateMutability":"nonpayable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[],"name":"MintFinished","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]')

def grants_transaction_validator(list_contributions):
    """This function check grants transaction list"""
    if isinstance(list_contributions, list):
        list_contrib = pd.DataFrame(list_contributions=list_contributions[1:, 1:], index=list_contributions[1:, 0],
                          columns=list_contributions[0, 1:])
        df = tuple(list_contrib)
    else:
        df = pd.read_csv(list_contributions, sep=" ")

    df.columns = [col.replace(',', '') for col in df.columns]
    check_transaction = lambda txid: w3.eth.getTransaction(txid)
    check_amount = lambda amount: int(amount[75:], 16) if len(amount) == 138 else print (f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_transaction} txid: {transaction_tax[:10]} -> status: 0 False - amount was off by 0.001 {bcolors.ENDC}")
    check_token = lambda token_address: len(token_address) == 42
    check_contract = lambda token_address, abi : w3.eth.contract(token_address, abi=abi)
    check_event_transfer =  lambda contract_address, search, txid : w3.eth.filter({ "address": contract_address, "topics": [search, txid]})
    get_decimals = lambda contract : int(contract.functions.decimals().call())

    # Colors for Console.
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    # scrapper settings
    ethurl = "https://etherscan.io/tx/"
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}

    # scrapes etherscan to get the replaced tx
    def getReplacedTX(tx):
        sleep(2)  # 2s delay to avoid getting the finger from etherscan
        response = requests.get(ethurl + tx, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        # look for span that contains the dropped&replaced msg
        p = soup.find("span", "u-label u-label--sm u-label--warning rounded")
        if "Replaced" in p.text:  # check if it's a replaced tx
            # get the id for the replaced tx
            q = soup.find(href=re.compile("/tx/0x"))
            return q.text
        else:
            return "dropped"

    def transaction_status(transaction, txid):
        """This function is core for check grants transaction list"""
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
        if (transfer_event or deposit_event or approve_event):
            print(
                f"{bcolors.OKGREEN} {index_element} txid: {txid[:10]} amount: {human_readable_value} {contract_symbol}   -> status: 1{bcolors.ENDC}")

    for index_transaction, index_valid in enumerate(df):
        for index_element, check_value in enumerate(df[index_valid]):
            if check_value is not None and not isinstance(check_value, float) and len(check_value) == 66:
                transaction_tax = check_value
                try:
                    transaction = check_transaction(transaction_tax)
                    token_address = check_token(transaction.to)
                    if (token_address):
                        transaction_status(transaction, transaction_tax)
                    else:
                        print (f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_element} txid: {transaction_tax[:10]} -> status: 0 - tx failed {bcolors.ENDC}")

                except TransactionNotFound:
                    rtx = getReplacedTX(transaction_tax)
                    if rtx == "dropped":
                        print (f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_element} txid: {transaction_tax[:10]} -> status: 0 - tx failed {bcolors.ENDC}")
                    else:
                        print(
                            f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_element} False, replaced with tx: {rtx[:10]} -> status: 0 - tx failed {bcolors.ENDC}")
                        print("\t↳", end='')
                        transaction_status(transaction, rtx)


                except:
                        transaction_receipt = w3.eth.getTransactionReceipt(transaction_tax)
                        if (transaction_receipt != None and transaction_receipt.cumulativeGasUsed >= 2100):
                            transaction_hash = transaction_receipt.transactionHash.hex()
                            transaction = check_transaction(transaction_hash)
                            if transaction.value > 0.001:
                                amount = w3.fromWei(transaction.value, 'ether')
                                print (f"{bcolors.OKGREEN} {index_element} txid: {transaction_tax[:10]} {amount} ETH -> status: 1 {bcolors.ENDC}")
                            else:
                                print (f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_element} txid: {transaction_tax[:10]} -> status: 0 - amount was off by 0.001 {bcolors.ENDC}")


if __name__ == '__main__':
    if (len(sys.argv) > 2):
        list_files = sys.argv
        for id, input_file in enumerate(list_files):
            if id > 0:
                grants_transaction_validator(input_file)
    else:
        grants_transaction_validator(sys.argv[1])


