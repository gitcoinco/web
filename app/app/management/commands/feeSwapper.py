import argparse
import time
import requests
import json
from web3 import Web3
#import factoryABI
#import tokenABI 
#import exchangeABI
from web3.middleware import geth_poa_middleware
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

#Amount of slippage from target Ether price from estimated price on exchange allowed when trading tokens back to ETH
SLIPPAGE = 0.05  

factoryABI = """[{"name": "NewExchange", "inputs": [{"type": "address", "name": "token", "indexed": true}, {"type": "address", "name": "exchange", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "initializeFactory", "outputs": [], "inputs": [{"type": "address", "name": "template"}], "constant": false, "payable": false, "type": "function", "gas": 35725}, {"name": "createExchange", "outputs": [{"type": "address", "name": "out"}], "inputs": [{"type": "address", "name": "token"}], "constant": false, "payable": false, "type": "function", "gas": 187911}, {"name": "getExchange", "outputs": [{"type": "address", "name": "out"}], "inputs": [{"type": "address", "name": "token"}], "constant": true, "payable": false, "type": "function", "gas": 715}, {"name": "getToken", "outputs": [{"type": "address", "name": "out"}], "inputs": [{"type": "address", "name": "exchange"}], "constant": true, "payable": false, "type": "function", "gas": 745}, {"name": "getTokenWithId", "outputs": [{"type": "address", "name": "out"}], "inputs": [{"type": "uint256", "name": "token_id"}], "constant": true, "payable": false, "type": "function", "gas": 736}, {"name": "exchangeTemplate", "outputs": [{"type": "address", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 633}, {"name": "tokenCount", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 663}]"""

tokenABI = """[{"name": "Transfer", "inputs": [{"type": "address", "name": "_from", "indexed": true}, {"type": "address", "name": "_to", "indexed": true}, {"type": "uint256", "name": "_value", "indexed": false}], "anonymous": false, "type": "event"}, {"name": "Approval", "inputs": [{"type": "address", "name": "_owner", "indexed": true}, {"type": "address", "name": "_spender", "indexed": true}, {"type": "uint256", "name": "_value", "indexed": false}], "anonymous": false, "type": "event"}, {"name": "__init__", "outputs": [], "inputs": [{"type": "bytes32", "name": "_name"}, {"type": "bytes32", "name": "_symbol"}, {"type": "uint256", "name": "_decimals"}, {"type": "uint256", "name": "_supply"}], "constant": false, "payable": false, "type": "constructor"}, {"name": "deposit", "outputs": [], "inputs": [], "constant": false, "payable": true, "type": "function", "gas": 74279}, {"name": "withdraw", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 108706}, {"name": "totalSupply", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 543}, {"name": "balanceOf", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "address", "name": "_owner"}], "constant": true, "payable": false, "type": "function", "gas": 745}, {"name": "transfer", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 74698}, {"name": "transferFrom", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_from"}, {"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 110600}, {"name": "approve", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_spender"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 37888}, {"name": "allowance", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "address", "name": "_owner"}, {"type": "address", "name": "_spender"}], "constant": true, "payable": false, "type": "function", "gas": 1025}, {"name": "name", "outputs": [{"type": "bytes32", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 723}, {"name": "symbol", "outputs": [{"type": "bytes32", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 753}, {"name": "decimals", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 783}]"""

exchangeABI = """[{"name": "TokenPurchase", "inputs": [{"type": "address", "name": "buyer", "indexed": true}, {"type": "uint256", "name": "eth_sold", "indexed": true}, {"type": "uint256", "name": "tokens_bought", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "EthPurchase", "inputs": [{"type": "address", "name": "buyer", "indexed": true}, {"type": "uint256", "name": "tokens_sold", "indexed": true}, {"type": "uint256", "name": "eth_bought", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "AddLiquidity", "inputs": [{"type": "address", "name": "provider", "indexed": true}, {"type": "uint256", "name": "eth_amount", "indexed": true}, {"type": "uint256", "name": "token_amount", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "RemoveLiquidity", "inputs": [{"type": "address", "name": "provider", "indexed": true}, {"type": "uint256", "name": "eth_amount", "indexed": true}, {"type": "uint256", "name": "token_amount", "indexed": true}], "anonymous": false, "type": "event"}, {"name": "Transfer", "inputs": [{"type": "address", "name": "_from", "indexed": true}, {"type": "address", "name": "_to", "indexed": true}, {"type": "uint256", "name": "_value", "indexed": false}], "anonymous": false, "type": "event"}, {"name": "Approval", "inputs": [{"type": "address", "name": "_owner", "indexed": true}, {"type": "address", "name": "_spender", "indexed": true}, {"type": "uint256", "name": "_value", "indexed": false}], "anonymous": false, "type": "event"}, {"name": "setup", "outputs": [], "inputs": [{"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 175875}, {"name": "addLiquidity", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "min_liquidity"}, {"type": "uint256", "name": "max_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": true, "type": "function", "gas": 82605}, {"name": "removeLiquidity", "outputs": [{"type": "uint256", "name": "out"}, {"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "amount"}, {"type": "uint256", "name": "min_eth"}, {"type": "uint256", "name": "min_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": false, "type": "function", "gas": 116814}, {"name": "__default__", "outputs": [], "inputs": [], "constant": false, "payable": true, "type": "function"}, {"name": "ethToTokenSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "min_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": true, "type": "function", "gas": 12757}, {"name": "ethToTokenTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "min_tokens"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": true, "type": "function", "gas": 12965}, {"name": "ethToTokenSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": true, "type": "function", "gas": 50455}, {"name": "ethToTokenTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": true, "type": "function", "gas": 50663}, {"name": "tokenToEthSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_eth"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": false, "type": "function", "gas": 47503}, {"name": "tokenToEthTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_eth"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": false, "type": "function", "gas": 47712}, {"name": "tokenToEthSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_bought"}, {"type": "uint256", "name": "max_tokens"}, {"type": "uint256", "name": "deadline"}], "constant": false, "payable": false, "type": "function", "gas": 50175}, {"name": "tokenToEthTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_bought"}, {"type": "uint256", "name": "max_tokens"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}], "constant": false, "payable": false, "type": "function", "gas": 50384}, {"name": "tokenToTokenSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 51007}, {"name": "tokenToTokenTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 51098}, {"name": "tokenToTokenSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 54928}, {"name": "tokenToTokenTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "token_addr"}], "constant": false, "payable": false, "type": "function", "gas": 55019}, {"name": "tokenToExchangeSwapInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 49342}, {"name": "tokenToExchangeTransferInput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}, {"type": "uint256", "name": "min_tokens_bought"}, {"type": "uint256", "name": "min_eth_bought"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 49532}, {"name": "tokenToExchangeSwapOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 53233}, {"name": "tokenToExchangeTransferOutput", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}, {"type": "uint256", "name": "max_tokens_sold"}, {"type": "uint256", "name": "max_eth_sold"}, {"type": "uint256", "name": "deadline"}, {"type": "address", "name": "recipient"}, {"type": "address", "name": "exchange_addr"}], "constant": false, "payable": false, "type": "function", "gas": 53423}, {"name": "getEthToTokenInputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_sold"}], "constant": true, "payable": false, "type": "function", "gas": 5542}, {"name": "getEthToTokenOutputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_bought"}], "constant": true, "payable": false, "type": "function", "gas": 6872}, {"name": "getTokenToEthInputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "tokens_sold"}], "constant": true, "payable": false, "type": "function", "gas": 5637}, {"name": "getTokenToEthOutputPrice", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "uint256", "name": "eth_bought"}], "constant": true, "payable": false, "type": "function", "gas": 6897}, {"name": "tokenAddress", "outputs": [{"type": "address", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1413}, {"name": "factoryAddress", "outputs": [{"type": "address", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1443}, {"name": "balanceOf", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "address", "name": "_owner"}], "constant": true, "payable": false, "type": "function", "gas": 1645}, {"name": "transfer", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 75034}, {"name": "transferFrom", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_from"}, {"type": "address", "name": "_to"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 110907}, {"name": "approve", "outputs": [{"type": "bool", "name": "out"}], "inputs": [{"type": "address", "name": "_spender"}, {"type": "uint256", "name": "_value"}], "constant": false, "payable": false, "type": "function", "gas": 38769}, {"name": "allowance", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [{"type": "address", "name": "_owner"}, {"type": "address", "name": "_spender"}], "constant": true, "payable": false, "type": "function", "gas": 1925}, {"name": "name", "outputs": [{"type": "bytes32", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1623}, {"name": "symbol", "outputs": [{"type": "bytes32", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1653}, {"name": "decimals", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1683}, {"name": "totalSupply", "outputs": [{"type": "uint256", "name": "out"}], "inputs": [], "constant": true, "payable": false, "type": "function", "gas": 1713}]"""


# Needed global variable - TO DO -- remove once fully integrated into Django


# Get all ERC-20 tokens and associated Uniswap Exchange addresses (if any).
# Returns a dict with keys being token ERC-20 contracts and associated name/symbol/Uniswap exchange address/wallet balance in that token
class Command(BaseCommand):
        help="Convert ERC-20 token balances in .env/FEE_ADDRESS to ETH where a Uniswap exchange is available"
        rpcProvider = ''
        tests = ''
        web3 = ''
        factoryContract = ''
        tokenList = ''

        def add_arguments(self, parser):
                # Optional arguments for testing
                parser.add_argument('-t','--test', action='store_true', help='Run on Rinkeby testnet')
                parser.add_argument('-r','--rpc', help='Provide RPC provider for web3 access')

        def getTokenList(self, walletAddress):
                
                if (self.tests == True): 
                        network = 'rinkeby'
                else:
                        network = 'mainnet'
                tokenList = {}
                print('https://blockscout.com/eth/'+network+'/api?module=account&action=tokenlist&address='+walletAddress)
                r = requests.get('https://blockscout.com/eth/'+network+'/api?module=account&action=tokenlist&address='+walletAddress)
                print(r.text)
                for transaction in r.json()['result']:
                        address = transaction['contractAddress']                      
                        exchangeAddress = self.factoryContract.functions.getExchange(self.web3.toChecksumAddress(address)).call()
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
                if (self.tests == True):
                        chain = 4
                else:
                        chain = 1
                exchangeContract = self.web3.eth.contract(address = exchangeAddress, abi = exchangeABI)
                tokenAddress = exchangeContract.functions.tokenAddress().call()
                tokenContract = self.web3.eth.contract(address = tokenAddress, abi = tokenABI)
                walletBalance = tokenContract.functions.balanceOf(settings.FEE_ADDRESS).call()
                if walletBalance == 0:
                        return
                outputReserve = self.web3.eth.getBalance(exchangeAddress)
                inputReserve = tokenContract.functions.balanceOf(exchangeAddress).call()
                numerator = walletBalance * outputReserve * 997
                denominator = inputReserve * 1000 + walletBalance * 997
                outputAmount = numerator / denominator
                deadline = self.web3.eth.getBlock('latest')['timestamp']+300
                self.stdout.write('Current token balance is : '+ str(self.web3.fromWei(walletBalance,'ether')))
                self.stdout.write('Amount of ETH to be bought is :' + str(self.web3.fromWei(outputAmount,'ether')))
                self.stdout.write('Exchange rate is : ' + str(outputAmount/walletBalance)+ ' ETH/token')

        ## Approve exchange to spend ERC-20 token balance
                nonce = self.web3.eth.getTransactionCount(settings.FEE_ADDRESS)
                txn_dict = exchangeContract.functions.approve(settings.FEE_ADDRESS,self.web3.toWei(walletBalance,'wei')).buildTransaction({
                        'chainId': chain,
                        'gas': 300000,
                        'gasPrice': self.web3.toWei(4,'gwei'),
                        'nonce':nonce,
                })
                signed_txn = self.web3.eth.account.signTransaction(txn_dict,private_key=settings.FEE_ADDRESS_PRIVATE_KEY)
                result = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
                tx_receipt = self.web3.eth.getTransactionReceipt(result)
                count = 0
                while tx_receipt is None and (count < 30):
                        time.sleep(10)
                        tx_receipt = self.web3.eth.getTransactionReceipt(result)
                print(tx_receipt)

        ## Submit token -> ETH exchange trade to Uniswap.  Transaction only works for BAT exchange on Rinkeby.
                nonce = self.web3.eth.getTransactionCount(settings.FEE_ADDRESS)
                txn_dict = exchangeContract.functions.tokenToEthSwapInput(self.web3.toWei(walletBalance,'wei'),self.web3.toWei(outputAmount*(1-SLIPPAGE),'wei'),deadline=deadline).buildTransaction({
                        'chainId': chain,
                        'gas': 300000,
                        'gasPrice': self.web3.toWei(4,'gwei'),
                        'nonce':nonce,
                })
                signed_txn = self.web3.eth.account.signTransaction(txn_dict,private_key=settings.FEE_ADDRESS_PRIVATE_KEY)
                result = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)

                tx_receipt = self.web3.eth.getTransactionReceipt(result)
                count = 0
                while tx_receipt is None and (count < 30):
                        time.sleep(10)
                        tx_receipt = self.web3.eth.getTransactionReceipt(result)

                print(tx_receipt)

# Arguments needed to run script.  Will convert to Django command once bugs are worked out

        def handle(self, **options):
                if options['test']:
                        self.tests = True
                else:
                        self.tests = False   
                
                self.rpcProvider=options['rpc']

                # Setup web3 connectivity
                if (self.tests == True):
                        self.web3 = Web3(Web3.HTTPProvider(self.rpcProvider))
                        self.factoryAddress = '0xf5D915570BC477f9B8D6C0E980aA81757A3AaC36'
                        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)

                else:
                        self.web3 = Web3(Web3.HTTPProvider(self.rpcProvider))
                        self.factoryAddress = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'


                self.factoryContract = self.web3.eth.contract(address = self.factoryAddress, abi = factoryABI)

                # Get all potential ERC-20 tokens that have associated Uniswap exchanges
                self.tokenList = self.getTokenList(settings.FEE_ADDRESS)
                # Loop through all tokens and swap to ETH
                for address, details in self.tokenList.items():
                        print(details['exchangeAddress'])
                        self.sell_token(details['exchangeAddress'])




