import argparse
import time
import requests
import json
from web3 import Web3
from ABIs.factoryABI import factoryABI
from ABIs.tokenABI import tokenABI 
from ABIs.exchangeABI import exchangeABI
from web3.middleware import geth_poa_middleware
from django.core.management.base import BaseCommand, CommandError

#Amount of slippage from target Ether price from estimated price on exchange allowed when trading tokens back to ETH
SLIPPAGE = 0.05  

# Needed global variable - TO DO -- remove once fully integrated into Django
privateKey = ''
walletAddress = ''
rpcProvider = ''
tests = ''
web3 = ''

# Get all ERC-20 tokens and associated Uniswap Exchange addresses (if any).
# Returns a dict with keys being token ERC-20 contracts and associated name/symbol/Uniswap exchange address/wallet balance in that token
class Command(BaseCommand):
        help="Convert ERC-20 token balances in .env/FEE_ADDRESS to ETH where a Uniswap exchange is available"

        def add_arguments(self, parser):
                # Optional arguments for testing
                parser.add_argument('-t','--test', action='store_true', help='Run on Rinkeby testnet')
                parser.add_argument('-w','--wallet', help='Provide the wallet address to use')
                parser.add_argument('-k','--key', help='Provide the private key for the wallet address to use')
                parser.add_argument('-r','--rpc', help='Provide RPC provider for web3 access')

        def getTokenList(self, walletAddress):
                if (tests == True): 
                        network = 'rinkeby'
                else:
                        network = 'mainnet'
                tokenList = {}
                r = requests.get('https://blockscout.com/eth/'+network+'/api?module=account&action=tokenlist&address='+walletAddress)
                for transaction in r.json()['result']:
                        address = transaction['contractAddress']                      
                        exchangeAddress = factoryContract.functions.getExchange(web3.toChecksumAddress(address)).call()
                        if exchangeAddress != '0x0000000000000000000000000000000000000000':
                                tokenList[address]={'tokenName':transaction['name'],'tokenSymbol':transaction['symbol'],'exchangeAddress':exchangeAddress,'balance':transaction['balance']}
                                self.stdout.write('Token Name: ' + tokenList[address]['tokenName']+ ' and Token Symbol is: ' + tokenList[address]['tokenSymbol'])
                                self.stdout.write('Token address is: ' + address)
                                self.stdout.write('Uniswap Exchange address is: '+ exchangeAddress)
                                self.stdout.write('Token balance is: ' + tokenList[address]['balance'])
                return tokenList


        # Swap total balance of ERC-20 token associated with Uniswap exchange address to ETH
        ## Doesn't work currently.
        def sell_token(self, exchangeAddress):
                if (tests == True):
                        chain = 4
                else:
                        chain = 1
                exchangeContract = web3.eth.contract(address = exchangeAddress, abi = exchangeABI)
                tokenAddress = exchangeContract.functions.tokenAddress().call()
                tokenContract = web3.eth.contract(address = tokenAddress, abi = tokenABI)
                walletBalance = tokenContract.functions.balanceOf(walletAddress).call()
                if walletBalance == 0:
                        return
                outputReserve = web3.eth.getBalance(exchangeAddress)
                inputReserve = tokenContract.functions.balanceOf(exchangeAddress).call()
                numerator = walletBalance * outputReserve * 997
                denominator = inputReserve * 1000 + walletBalance * 997
                outputAmount = numerator / denominator
                deadline = web3.eth.getBlock('latest')['timestamp']+300
                self.stdout.write('Current token balance is : '+ str(web3.fromWei(walletBalance,'ether')))
                self.stdout.write('Amount of ETH to be bought is :' + str(web3.fromWei(outputAmount,'ether')))
                self.stdout.write('Exchange rate is : ' + str(outputAmount/walletBalance)+ ' ETH/token')

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
                self.stdout.write(tx_receipt)

        ## Submit token -> ETH exchange trade to Uniswap.  Transaction only works for BAT exchange on Rinkeby.
                nonce = web3.eth.getTransactionCount(walletAddress)
                txn_dict = exchangeContract.functions.tokenToEthSwapInput(web3.toWei(walletBalance,'wei'),web3.toWei(outputAmount*(1-SLIPPAGE),'wei'),deadline=deadline).buildTransaction({
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

                self.stdout.write(tx_receipt)

# Arguments needed to run script.  Will convert to Django command once bugs are worked out

        def handle(**options):
                if options['test']:
                        tests = True
                else:
                        tests = False   

                walletAddress=options['wallet']
                privateKey=options['key']
                rpcProvider=options['rpc']

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
                        self.stdout.write (details['exchangeAddress'])
                        sell_token(details['exchangeAddress'])




