import datetime as dt
from datetime import timezone
from time import sleep

import requests

api_key = '' # add an etherscan api key here

tx_url = 'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={}&apikey=' + api_key
ct_check_url = 'https://api.etherscan.io/api?module=transaction&action=getstatus&txhash={}&apikey=' + api_key
tx_check_url = 'https://api.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={}&apikey=' + api_key
tx_receipt_url = 'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionReceipt&txhash={}&apikey=' + api_key

#USD coin, Rchain token
address_conversions= {'0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 1000000, "0x168296bb09e24a88805cb9c33356536b980d3fc5": 100000000}

def valid_contract(txid):
    contract_status = requests.get(ct_check_url.format(txid))
    contract_status = contract_status.json().get('result')['isError']
    return contract_status == '0' 

def valid_transaction(txid):
    tx_status = requests.get(tx_check_url.format(txid))
    tx_status = tx_status.json().get('status')
    return tx_status == '1'

def get_token_amount(amount, token_address):
    if token_address in address_conversions:
        tokens = float(int(amount, 16)/address_conversions[token_address])
    else:
        tokens = float(int(amount, 16)/1000000000000000000)
    return tokens


def check_transaction(txid, amount_total, amount_minus_gitcoin_fee, token_address):
    r = requests.get(tx_url.format(txid))
    r_data = r.json().get('result')

    # This is a dropped / replaced txn
    if not r_data:
        #TODO
        return (0, 'txn not found', txid)

    # ETH 
    if token_address == "0x0000000000000000000000000000000000000000":
        if valid_transaction(txid) == False:
            return (0, 'transaction failure', txid)
        amount = r_data['value'] 
        
    # ERC20
    else: 
        amount = float('inf')
        #if address doesn't match, must check events :
        if r_data['to'] != token_address:
            r = requests.get(tx_receipt_url.format(txid))
            for d in (r.json()['result'])['logs']:
                if d['address'] == token_address:
                    amount = d['data']
                    break
            if amount == float('inf'):
                return (0, 'incorrect address', txid)
        else:
            amount = r_data['input']
            amount = amount[-64:]

        if valid_transaction(txid) == False:
            return (0, 'transaction failure', txid)
        elif valid_contract(txid) == False:
            return (0, 'contract failure', txid)

    tokens = get_token_amount(amount, token_address)

    # less than .001 difference is ok
    diff1 = tokens - float(amount_total) 
    diff2 = tokens - float(amount_minus_gitcoin_fee) 
    if diff1 <= -.001 and diff2 <= -.001 :
        return (0, 'incorrect amount off by {}'.format(diff1), txid)

    return (1, 'success')



if __name__ == "__main__":
    filepath = "test_input.txt"
    with open(filepath) as fp:
        fp.readline()
        fp.readline()
        line = fp.readline()
        while line:
            line = fp.readline()
            line = line.split(" ")
            print(check_transaction(line[0], line[1], line[2], line[3].lower().strip()))

