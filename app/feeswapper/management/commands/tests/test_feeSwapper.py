import json
from datetime import datetime
from unittest import mock

from django.core.management import call_command

import pytz
from feeswapper.management.commands.feeSwapper import Command
from feeswapper.models import CurrencyConversion
from test_plus.test import TestCase


class RequestsMockResponse:
    def __init__(self, status_code, json_data=None):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = True

    def json(self):
        return self.json_data

class feeSwapperTest(TestCase):
    """Define tests for feeSwapper management command."""

    resp = RequestsMockResponse(200,json_data=
    {"status":"1","result":[
        {
            "symbol":"OMG",
            "name":"OMGToken",
            "decimals":"18",
            "contractAddress":"0x879884c3c46a24f56089f3bbbe4d5e38db5788c0",
            "balance":"10000000"
        },
        {
            "symbol":"WEENUS",
            "name":"Weenus 💪",
            "decimals":"18",
            "contractAddress":"0xaff4481d10270f50f203e0763e2597776068cbc5",
            "balance":"1000000000000000000000"
        },
        {
            "symbol":"BAT",
            "name":"Basic Attention Token",
            "decimals":"18",
            "contractAddress":"0xda5b056cfb861282b4b59d29c9b395bcc238d29b",
            "balance":"10"
        },
        {
            "symbol":"MKR",
            "name":"Maker",
            "decimals":"18",
            "contractAddress":"0xf9ba5210f91d0474bd1e1dcdaec4c58e359aad85",
            "balance":"0"
        }],
        "message":"OK"
    })
    
    @mock.patch('feeswapper.management.commands.feeSwapper.requests.get',return_value=resp)
    @mock.patch('feeswapper.management.commands.feeSwapper.Command.factoryContract', return_value="0x0000000000000000000000000000000000000001")
    @mock.patch('feeswapper.management.commands.feeSwapper.Command.web3', return_value='1')
    def test_getTokenList(self, response, web3_response, toWei_response):
        """Test getTokenList returns proper dictionary with expected token values."""
        tokenList = Command().getTokenList()
        assert tokenList["0xda5b056cfb861282b4b59d29c9b395bcc238d29b"]["tokenSymbol"] == "BAT"

    @mock.patch('feeswapper.management.commands.feeSwapper.requests.get',return_value=resp)
    @mock.patch('feeswapper.management.commands.feeSwapper.Command.factoryContract', return_value="0x0000000000000000000000000000000000000001")
    @mock.patch('feeswapper.management.commands.feeSwapper.Command.web3', return_value='1')
    def test_getTokenList_with_zero_balance_token(self, response, web3_response, toWei_response):
        """Test getTokenList returns no key for a token with a zero balance."""
        tokenList = Command().getTokenList()
        with self.assertRaises(KeyError):
            tokenList["0xf9ba5210f91d0474bd1e1dcdaec4c58e359aad85"]

    @mock.patch('feeswapper.management.commands.feeSwapper.Command.web3', return_value='1')
    @mock.patch('feeswapper.management.commands.feeSwapper.Command.sg', return_value='1')
    def test_sell_token_with_previous_failed_fee_swap(self, web3_response, sg_response):
        """Verify that sell_token function doesn't attempt to swap a balance on a token with a previous failed token swap."""
        CurrencyConversion.objects.create(
            transaction_result="failure",
            from_token_symbol="MKR",
            to_token_symbol="ETH",
            from_amount=1,
            to_amount=1,
            conversion_rate=1,
            txid="ABC",
            from_token_addr="0x1",
            transaction_date=datetime(2008, 10, 31, tzinfo=pytz.UTC)
        )
        Command().sell_token("0x1","MKR")
        assert CurrencyConversion.objects.filter(from_token_symbol="MKR").count() == 1
    
    @mock.patch('feeswapper.management.commands.feeSwapper.Command.web3')
    def test_sell_token_with_successful_trade(self, web3_response):
        """Verify that sell_token function posts a successful trade record to Currency Conversion table after successful transaction and 
        that output amount is calculated correctly given the inputs (ERC-20 token balance, Uniswap ETH reserve )."""
        eth_Mock = mock.Mock()
        call_Mock = mock.Mock(return_value=1000)
        balanceOf_Mock = mock.Mock()
        balanceOf_Mock.attach_mock(call_Mock,'call')
        contract_Mock = mock.Mock()
        contract_Mock.functions.balanceOf.return_value=balanceOf_Mock
        contract_Mock.functions.tokenAddress.return_value=balanceOf_Mock
        eth_Mock.contract.return_value=contract_Mock
        web3_response.attach_mock(eth_Mock,'eth')
        web3_response.fromWei.return_value="1000"
        web3_response.eth.getBalance.return_value=1000
        web3_response.eth.getBlock.return_value={'timestamp':9999999}
        web3_response.eth.getTransactionReceipt.return_value = {
            "status":1,
            "transactionHash":"0x1"
        }
        
        web3_response.toHex.return_value="0x12234"
        Command().sell_token("0x1","BAT")
        assert CurrencyConversion.objects.filter(from_token_symbol="BAT").count() == 1
        assert CurrencyConversion.objects.filter(from_token_symbol="BAT")[0].to_amount == 499.248873309965
