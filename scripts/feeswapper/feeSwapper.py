import argparse
import time
import requests
import json
from web3 import Web3
from factoryABI import factoryABI
from tokenABI import tokenABI 
from exchangeABI import exchangeABI
from web3.middleware import geth_poa_middleware


# Get all ERC-20 tokens and associated Uniswap Exchange addresses (if any).
# Returns a dict with keys being token ERC-20 contracts and associated name/symbol/Uniswap exchange address/wallet balance in that token

def getTokenList(walletAddress):
        if (tests == True): 
                network = 'rinkeby'
        else:
                network = 'mainnet'
        tokenList = {}
        r = requests.get('https://blockscout.com/eth/'+network+'/api?module=account&action=tokenlist&address='+walletAddress)
        for transaction in r.json()['result']:
                address = transaction['contractAddress']
                if address not in tokenList:                        
                        exchangeAddress = factoryContract.functions.getExchange(web3.toChecksumAddress(address)).call()
                        if exchangeAddress != '0x0000000000000000000000000000000000000000':
                                tokenList[address]={'tokenName':transaction['name'],'tokenSymbol':transaction['symbol'],'exchangeAddress':exchangeAddress,'balance':transaction['balance']}
                                print('Token Name: ' + tokenList[address]['tokenName']+ ' and Token Symbol is: ' + tokenList[address]['tokenSymbol'])
                                print('Token address is: ' + address)
                                print('Uniswap Exchange address is: '+ exchangeAddress)
                                print('Token balance is: ' + tokenList[address]['balance'])
        return tokenList


# Swap total balance of ERC-20 token associated with Uniswap exchange address to ETH
## Doesn't work currently.
def sell_token(exchangeAddress):
        if (tests == True):
                chain = 4
        else:
                chain = 1
        exchangeContract = web3.eth.contract(address = exchangeAddress, abi = exchangeABI)
        tokenAddress = exchangeContract.functions.tokenAddress().call()
        tokenContract = web3.eth.contract(address = tokenAddress, abi = tokenABI)
        walletBalance = tokenContract.functions.balanceOf(walletAddress).call()
        outputReserve = web3.eth.getBalance(exchangeAddress)
        inputReserve = tokenContract.functions.balanceOf(exchangeAddress).call()
        numerator = walletBalance * outputReserve * 997
        denominator = inputReserve * 1000 + walletBalance * 997
        outputAmount = numerator / denominator
        deadline = web3.eth.getBlock('latest')['timestamp']+300
        print('Current token balance is : '+ str(web3.fromWei(walletBalance,'ether')))
        print('Amount of ETH to be bought is :' + str(web3.fromWei(outputAmount,'ether')))
        print('Exchange rate is : ' + str(outputAmount/walletBalance)+ ' ETH/token')

## Approve exchange to spend ERC-20 token balance
        nonce = web3.eth.getTransactionCount(walletAddress)
        txn_dict = exchangeContract.functions.approve(walletAddress,web3.toWei(walletBalance,'wei')).buildTransaction({
                'chainId': chain,
                'gas': 300000,
                'gasPrice': web3.toWei(4,'gwei'),
                'nonce':nonce,
        })
        signed_txn = web3.eth.account.signTransaction(txn_dict,private_key=privateKey)
        result = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        tx_receipt = web3.eth.getTransactionReceipt(result)
        count = 0
        while tx_receipt is None and (count < 30):
                time.sleep(10)
                tx_receipt = web3.eth.getTransactionReceipt(result)
        print(tx_receipt)

## Submit token -> ETH exchange trade to Uniswap with 5% slippage.  Transaction always fails.
        nonce = web3.eth.getTransactionCount(walletAddress)
        txn_dict = exchangeContract.functions.tokenToEthSwapInput(web3.toWei(walletBalance,'wei'),web3.toWei(outputAmount*0.95,'wei'),deadline=deadline).buildTransaction({
                'chainId': chain,
                'gas': 300000,
                'gasPrice': web3.toWei(4,'gwei'),
                'nonce':nonce,
        })
        signed_txn = web3.eth.account.signTransaction(txn_dict,private_key=privateKey)
        result = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

        tx_receipt = web3.eth.getTransactionReceipt(result)
        count = 0
        while tx_receipt is None and (count < 30):
                time.sleep(10)
                tx_receipt = web3.eth.getTransactionReceipt(result)

        print(tx_receipt)

# Arguments needed to run script.  Will convert to Django command once bugs are worked out
parser = argparse.ArgumentParser(description='Fee Address Altcoint Swapper')
parser.add_argument('-t','--test', action='store_true', help='Run on Rinkeby testnet', required=False)
parser.add_argument('-w','--wallet', help='Provide the wallet address to use', required=True)
parser.add_argument('-k','--key', help='Provide the private key for the wallet address to use', required=True)
parser.add_argument('-r','--rpc', help='Provide RPC provider for web3 access', required=True)
args = vars(parser.parse_args())
if args['test']:
        tests = True
else:
        tests = False

walletAddress=args['wallet']
privateKey=args['key']
rpcProvider=args['rpc']

# Setup web3 connectivity
if (tests == True):
        web3 = Web3(Web3.HTTPProvider(rpcProvider))
        factoryAddress = '0xf5D915570BC477f9B8D6C0E980aA81757A3AaC36'
        web3.middleware_stack.inject(geth_poa_middleware, layer=0)

else:
        web3 = Web3(Web3.HTTPProvider(rpcProvider))
        factoryAddress = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'


factoryContract = web3.eth.contract(address = factoryAddress, abi = factoryABI)

# Get all potential ERC-20 tokens that have associated Uniswap exchanges
tokenList = getTokenList(walletAddress)
# Loop through all tokens and swap to ETH
for address, details in tokenList.items():
        print (details['exchangeAddress'])
        sell_token(details['exchangeAddress'])


