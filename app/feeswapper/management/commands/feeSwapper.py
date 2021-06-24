'''
    Copyright (C) 2021 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

import json
import logging
import time
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

import requests
import sendgrid
from feeswapper.models import CurrencyConversion
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from sendgrid.helpers.mail import Content, Email, Mail
from web3 import Web3
from web3.middleware import geth_poa_middleware

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Command(BaseCommand):
        """ Check FEE_ADDRESS for ERC-20 token balances and tries to convert to ETH using Uniswap if exchange is available"""

        help="Convert ERC-20 token balances in .env/FEE_ADDRESS to ETH where a Uniswap exchange is available"

        network = ''   
        web3 = ''
        factoryContract = ''
        tokenList = ''
        factoryABI = ''
        tokenABI = ''
        exchangeABI = ''
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        
        def getTokenList(self):
                """ Query the blockscout API for ERC-20 token balances.

                Returns:
                  tokenList: A dict with the key being the ERC-20 token address and the value being an object containing
                  the token name, token symbol, Uniswap exchange address, and the token balance held by the FEE_ADDRESS

                """
                tokenList = {}
                r = requests.get('https://blockscout.com/eth/'+self.network+'/api?module=account&action=tokenlist&address='+settings.FEE_ADDRESS)
                logger.info(json.dumps(r.json()))

                # Check if API is functioning and returned any ERC-20 tokens associated with the FEE_ADDRESS and return null token list if not.
                if not r.ok or r.json()['status'] != '1':
                        return {}
                
                for transaction in r.json()['result']:
                        if int(transaction['balance'])>0:
                                address = transaction['contractAddress']                      
                                exchangeAddress = self.factoryContract.functions.getExchange(self.web3.toChecksumAddress(address)).call()
                                if exchangeAddress != '0x0000000000000000000000000000000000000000':
                                        # Only add token to list to ETH if Uniswap exchange exists
                                        tokenList[address]={'tokenName':transaction['name'],'tokenSymbol':transaction['symbol'],'exchangeAddress':exchangeAddress,'balance':transaction['balance']}
                                        logger.info('Token Name: ' + tokenList[address]['tokenName']+ ' and Token Symbol is: ' + tokenList[address]['tokenSymbol'])
                                        logger.info('Token address is: ' + address)
                                        logger.info('Uniswap Exchange address is: '+ exchangeAddress)
                                        logger.info('Token balance is: ' + tokenList[address]['balance'])
                return tokenList

        def sell_token(self, exchangeAddress, tokenSymbol):
                """Swap total balance of ERC-20 token associated with Uniswap exchange address to ETH.
                
                Args:
                        exchangeAddress (str): The address of the Uniswap exchange contract assocciated with the ERC-20 token to convert to ETH
                        tokenSymbol (str): The symbol for the ERC-20 token to be converted to ETH. 
                
                Note: This currently only works with the BAT Uniswap exchange on Rinkeby Testnet
                """
                if (self.network == 'rinkeby'):
                        chain = 4
                else:
                        chain = 1

     
                # Check for previous failed transactions in database
                failure_count = CurrencyConversion.objects.filter(from_token_symbol=tokenSymbol).exclude(transaction_result='success').count()
                if failure_count == 0:

                        exchangeContract = self.web3.eth.contract(address = exchangeAddress, abi = self.exchangeABI)
                        tokenAddress = exchangeContract.functions.tokenAddress().call() 
                        # Follows Uniswap doc guidance on calculating conversion
                        tokenContract = self.web3.eth.contract(address = tokenAddress, abi = self.tokenABI)
                        walletBalance = tokenContract.functions.balanceOf(settings.FEE_ADDRESS).call()
                        outputReserve = self.web3.eth.getBalance(exchangeAddress)
                        inputReserve = tokenContract.functions.balanceOf(exchangeAddress).call()
                        numerator = walletBalance*outputReserve * (1-settings.UNISWAP_LIQUIDITY_FEE)*1000
                        denominator = inputReserve*1000 + walletBalance*(1-settings.UNISWAP_LIQUIDITY_FEE)*1000
                        outputAmount = numerator / denominator
                        deadline = self.web3.eth.getBlock('latest')['timestamp'] + settings.UNISWAP_TRADE_DEADLINE
                        logger.info('Current token balance is : ' + str(self.web3.fromWei(walletBalance,'ether')))
                        logger.info('Amount of ETH to be bought is :' + str(self.web3.fromWei(outputAmount,'ether')))
                        logger.info('Exchange rate is : ' + str(outputAmount/walletBalance)+ ' ETH/token')

                        # Call contract function to give exchange approval to spend ERC-20 token balance.  
                        # Required to have exchange perform ERC-20 token transactions on behalf of FEE_ADDRESS
                        nonce = self.web3.eth.getTransactionCount(settings.FEE_ADDRESS)
                        txn_dict = exchangeContract.functions.approve(settings.FEE_ADDRESS,self.web3.toWei(walletBalance,'wei')).buildTransaction({
                                'chainId': chain,
                                'gas': 300000,
                                'gasPrice': self.web3.toWei(recommend_min_gas_price_to_confirm_in_time(settings.UNISWAP_TRADE_DEADLINE/60),'gwei'),
                                'nonce':nonce,
                        })
                        logger.info(txn_dict)
                        signed_txn = self.web3.eth.account.signTransaction(txn_dict,private_key=settings.FEE_ADDRESS_PRIVATE_KEY)
                        result = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
                        tx_receipt = self.web3.eth.getTransactionReceipt(result)
                        count = 0
                        while tx_receipt is None and (count < 30):
                                time.sleep(10)
                                tx_receipt = self.web3.eth.getTransactionReceipt(result)
                        logger.info(str(tx_receipt))

                        # Submit token -> ETH exchange trade to Uniswap.  Transaction only works for BAT exchange on Rinkeby.
                        nonce = self.web3.eth.getTransactionCount(settings.FEE_ADDRESS)
                        txn_dict = exchangeContract.functions.tokenToEthSwapInput(self.web3.toWei(walletBalance,'wei'),self.web3.toWei(outputAmount*(1-settings.SLIPPAGE),'wei'),deadline=deadline).buildTransaction({
                                'chainId': chain,
                                'gas': 300000,
                                'gasPrice': self.web3.toWei(recommend_min_gas_price_to_confirm_in_time(settings.UNISWAP_TRADE_DEADLINE/60),'gwei'),
                                'nonce':nonce,
                        })
                        signed_txn = self.web3.eth.account.signTransaction(txn_dict,private_key=settings.FEE_ADDRESS_PRIVATE_KEY)
                        result = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)

                        tx_receipt = self.web3.eth.getTransactionReceipt(result)
                        count = 0
                        while tx_receipt is None and (count < 30):
                                time.sleep(10)
                                tx_receipt = self.web3.eth.getTransactionReceipt(result)

                        logger.info(str(tx_receipt))

                        if tx_receipt['status'] == 1:
                                # Post transaction record to database if transaction succeeded
                                transaction_record = CurrencyConversion.objects.create(transaction_date=now(),from_amount=walletBalance, to_amount=outputAmount,conversion_rate=outputAmount/walletBalance,txid=self.web3.toHex(tx_receipt['transactionHash']),from_token_addr=tokenAddress,from_token_symbol=tokenSymbol,to_token_symbol='ETH',transaction_result='success')
                        else:
                                # Post failed transaction record to database if transaction failed
                                transaction_record = CurrencyConversion.objects.create(transaction_date=now(),from_amount=walletBalance, to_amount=outputAmount,conversion_rate=outputAmount/walletBalance,txid=self.web3.toHex(tx_receipt['transactionHash']),from_token_addr=tokenAddress,from_token_symbol=tokenSymbol,to_token_symbol='ETH',transaction_result='failure')
                                # Email Gitcoin staff if transaction failed
                                mail = Mail(Email(settings.CONTACT_EMAIL),'Failed fee conversion', Email(settings.CONTACT_EMAIL),Content('text/plain', tokenSymbol+' conversion to ETH failed'))
                                response = self.sg.client.mail.send.post(request_body=mail.get())
                else:
                        return # this email always fails.. disabling it
                        # Email Gitcoin staff if token balance exists in wallet where previous attempt convert to ETH failed
                        mail = Mail(Email('kevin@gitcoin.co'),'Token in Fee Wallet with previous failed fee conversion', Email(settings.CONTACT_EMAIL),Content('text/plain', tokenSymbol+' conversion to ETH failed previously so no conversion was attempted.'))                        
                        response = self.sg.client.mail.send.post(request_body=mail.get())
                        

        def handle(self, **options):
                """ Execute main management command function.
                
                Returns:
                        tokenList: Dict containing all ERC-20 tokens held by the FEE_ADDRESS and their balances

                """
                if settings.DEBUG:
                        self.network = 'rinkeby'
                else:
                        self.network = 'mainnet' 

                # Setup web3 connectivity
                self.web3 = Web3(Web3.HTTPProvider(settings.WEB3_HTTP_PROVIDER+'/v3/'+settings.INFURA_V3_PROJECT_ID))
                
                if (self.network == 'rinkeby'):
                        self.factoryAddress = '0xf5D915570BC477f9B8D6C0E980aA81757A3AaC36'
                        self.web3.middleware_stack.inject(geth_poa_middleware, layer=0)

                else:
                        self.factoryAddress = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'

                # Set up factory contract
                with open("feeswapper/management/commands/factoryABI.json","r") as factoryABIfile:
                        self.factoryABI = json.load(factoryABIfile)
                self.factoryContract = self.web3.eth.contract(address = self.factoryAddress, abi = self.factoryABI)

                # Get token and contract ABIs
                with open("feeswapper/management/commands/tokenABI.json","r") as tokenABIfile:
                        self.tokenABI = json.load(tokenABIfile)
                with open("feeswapper/management/commands/exchangeABI.json","r") as exchangeABIfile:
                        self.exchangeABI = json.load(exchangeABIfile)
                
                
                # Get all potential ERC-20 tokens that have associated Uniswap exchanges
                self.tokenList = self.getTokenList()
                # Loop through all tokens and swap to ETH
                for address, details in self.tokenList.items():
                        logger.info(details['exchangeAddress'])
                        self.sell_token(details['exchangeAddress'],details['tokenSymbol'])
                        
                if self.network == 'rinkeby':
                        return json.dumps(self.tokenList)
                else:
                        return str(self.tokenList)
