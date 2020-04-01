import csv
import os
import re
import requests
from bs4 import BeautifulSoup
from time import sleep
from web3 import Web3
from web3.exceptions import (
    TransactionNotFound,
)

# setting up infura as our web3 provider
INFURA_TOKEN = os.getenv("INFTOKEN")
web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/{0}".format(INFURA_TOKEN)))

# we save token decimal details here
token_details = {}

# scrapper settings
ethurl = "https://etherscan.io/tx/"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}

# scrapes etherscan to get the replaced tx
def getReplacedTX(tx):
    sleep(2) # 2s delay to avoid getting the finger from etherscan
    response = requests.get(ethurl + tx, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    # look for span that contains the dropped&replaced msg
    p = soup.find("span", "u-label u-label--sm u-label--warning rounded")
    if "Replaced" in p.text: # check if it's a replaced tx
        # get the id for the replaced tx
        q = soup.find(href=re.compile("/tx/0x"))
        return q.text
    else:
        return "dropped"

# uses ethplorer api to get token decimals of any token contract
def getTokenDecimals(addr):
   if not addr in token_details:
        data = requests.get(('http://api.ethplorer.io/getTokenInfo/{0}?apiKey=freekey').format(addr)).json()
        try:
            token_details[addr] = int(data['decimals'])
        except KeyError: # not a token contract
            token_details[addr] = -1
   return token_details[addr]

def checkTransaction(txid, correct_amount, correct_amount_fee, token_address):
    print("[ " + txid[:16] + " ] ", end='')
    try:
        prov = web3.eth.getTransaction(txid)

        from_address = prov['from'].lower()
        to_address = prov.to.lower()
        token_address = token_address.lower()

        if (from_address == to_address): # check if tx got replaced by sending a 0 eth tx to same address
            print("False, tx to same address")
            return

        if (token_address == "0x0000000000000000000000000000000000000000"):
            pass
        elif (to_address != token_address): # check if token address doesn't match tx
            prov2 = web3.eth.getTransactionReceipt(txid) # check the logs
            ok_tx = False
            for index in prov2.logs: 
                if (index.address.lower() == token_address):
                    ok_tx = True
                    break
            if ok_tx:
                pass
            else:
                print("Failed, tx sent to wrong address")
                return
        
        amount = float(correct_amount)
        amount_fee = float(correct_amount_fee)
        if (prov.value == 0): # token transaction
            token_decimals = getTokenDecimals(to_address)
            tx_amount = int(prov.input[-64:], 16) / (10**token_decimals)
            if (tx_amount < amount):
                print("False, amount off by", round(amount - tx_amount, token_decimals-1))
            elif (tx_amount < amount_fee):
                print("False, amount off by", round(amount_fee - tx_amount, token_decimals-1))
            else:
                print("True")
        else: # eth transaction
            tx_amount = prov.value / 1e18
            if (tx_amount < amount):
                print("False, amount off by", round(amount - tx_amount, 16))
            elif (tx_amount < amount_fee):
                print("False, amount off by", round(amount_fee - tx_amount, 16))
            else:
                print("True")
    except TransactionNotFound: # if getTransaction fails, use the etherscan scraper
        rtx = getReplacedTX(txid)
        if rtx == "dropped":
            print("False, tx failed")
        else:
            print("False, replaced with tx:", rtx)
            print("\t↳", end='')
            checkTransaction(rtx, correct_amount, correct_amount_fee, token_address)

with open('contributions.txt', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ')
    next(reader, None)
    for row in reader:
        if row:
            checkTransaction(row[0], row[1], row[2], row[3])