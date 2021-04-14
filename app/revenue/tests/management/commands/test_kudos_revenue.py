#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Handle dashboard embed related tests.

Copyright (C) 2018 Gitcoin Core

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

"""

import json
import os
from unittest.mock import Mock, patch

from django.conf import settings

from revenue.management.commands.kudos_revenue import Command, call_etherscan_api
from revenue.models import DigitalGoodPurchase
from test_plus.test import TestCase


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, ok, status_code, reason='Fail'):
            self.ok = ok
            self.json_data = json_data
            self.status_code = status_code
            self.reason = reason

        def json(self):
            return self.json_data

    params = args[1]
    if params['action'] == 'txlist':
        with open(os.path.join(os.path.dirname(__file__), 'txlist_sample.json')) as json_file:
            return MockResponse(json.load(json_file), True, 200)
    elif params['action'] == 'tokentx':
        with open(os.path.join(os.path.dirname(__file__), 'tokentx_sample.json')) as json_file:
            return MockResponse(json.load(json_file), True, 200)
    return MockResponse(None, False, 404)


class TestKudosRevenue(TestCase):

    def setUp(self):
        default_account = settings.KUDOS_REVENUE_ACCOUNT_ADDRESS
        self.account = default_account if len(default_account) > 0 else '0xAD278911Ad07534F921eD7D757b6c0e6730FCB16'


    @patch('revenue.management.commands.kudos_revenue.requests.get')
    def test_etherscan_account_txlist_api_call(self, mock_func):
        """Test etherscan txlist api call """
        mock_func.return_value = Mock(ok=True)
        mock_func.return_value.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "blockNumber": "6570004",
                    "timeStamp": "1540317632",
                    "hash": "0x84a4a80b6e70048bf0ee8b937a4931efdb4f30e248e0f15036cf40748aef938e",
                    "nonce": "4",
                    "blockHash": "0x9b9d524c5fb92ed79fac4174c8136b9a11527cf7ba30985a27502c104bb6c574",
                    "transactionIndex": "95",
                    "from": "0xf8ae578d5d4e570de6c31f26d42ef369c320ae0b",
                    "to": "0xAD278911Ad07534F921eD7D757b6c0e6730FCB16",
                    "value": "50000000000000000",
                    "gas": "21000",
                    "gasPrice": "4000000000",
                    "isError": "0",
                    "txreceipt_status": "1",
                    "input": "0x",
                    "contractAddress": "",
                    "cumulativeGasUsed": "7992355",
                    "gasUsed": "21000",
                    "confirmations": "2546337"
                }
            ]
        }
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': self.account,
            'startblock': 0,
            'endblock': 6570004,
            'apikey': settings.ETHERSCAN_API_KEY,
            'sort': 'asc',
            }
        records = call_etherscan_api('mainnet', params)
        self.assertTrue(len(records) == 1)
        for record in records:
            self.assertTrue('hash' in record)
            self.assertTrue('contractAddress' in record)
            self.assertTrue('value' in record)
            self.assertTrue('from' in record)
            self.assertTrue('to' in record)
            break


    '''@patch('revenue.management.commands.kudos_revenue.call_etherscan_api')
    def test_etherscan_account_tokentx_api_call(self, mock_func):
        """Test etherscan tokentx api call """
        mock_func.return_value = Mock(ok=True)
        mock_func.return_value.json.return_value = {
            "blockNumber": "6966980",
            "timeStamp": "1545985587",
            "hash": "0x5a852c0437b1db68de3551c335d6c1399a5c0b82516b5bf71d6b80df54f26d02",
            "nonce": "203",
            "blockHash": "0x1c0ce49c6d06420bbbf877db1a42681d722c3e2dc885335ff8215bbdd0f3f4de",
            "from": "0x1615aecb476aec5f6066dcf2e80716ccf0e7345c",
            "contractAddress": "0x85332b222787eacab0fff68cf3b884798823528c",
            "to": "0xAD278911Ad07534F921eD7D757b6c0e6730FCB16",
            "value": "666",
            "tokenName": "WinETHFree",
            "tokenSymbol": "winethfree.com (Win ETH Free)",
            "tokenDecimal": "0",
            "transactionIndex": "2",
            "gas": "2000000",
            "gasPrice": "3000000000",
            "gasUsed": "1702798",
            "cumulativeGasUsed": "6090923",
            "input": "deprecated",
            "confirmations": "2149742"
        }
        params = {
            'module': 'account',
            'action': 'tokentx',
            'address': self.account,
            'startblock': 0,
            'endblock': 6966980,
            'apikey': settings.ETHERSCAN_API_KEY,
            'sort': 'asc',
            }
        records = call_etherscan_api('mainnet', params)
        self.assertTrue(len(records) == 1)
        for record in records:
            self.assertTrue('hash' in record)
            self.assertTrue('contractAddress' in record)
            self.assertTrue('value' in record)
            self.assertTrue('from' in record)
            self.assertTrue('to' in record)
            self.assertTrue('tokenDecimal' in record)
            self.assertTrue('tokenSymbol' in record)
            break'''


    @patch('revenue.management.commands.kudos_revenue.requests.get')
    def test_etherscan_account_wrong_api_call(self, mock_func):
        """Test wrong call to etherscan api """
        mock_func.return_value = Mock(ok=False)
        params = {
            'module': 'account',
            'action': 'transactions', # non-existent action
            'address': self.account,
            'startblock': 0,
            'endblock': 6570004,
            'apikey': settings.ETHERSCAN_API_KEY,
            'sort': 'asc',
            }
        records = call_etherscan_api('mainnet', params)
        self.assertTrue(len(records) == 0)


    @patch('revenue.management.commands.kudos_revenue.requests.get')
    def test_etherscan_account_no_tx_found_api_call(self, mock_func):
        """Test no records found during etherscan api call """
        mock_func.return_value = Mock(ok=False)
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': self.account,
            'startblock': 0,
            'endblock': 6,
            'apikey': settings.ETHERSCAN_API_KEY,
            'sort': 'asc',
            }
        records = call_etherscan_api('mainnet', params)
        self.assertTrue(len(records) == 0)


    @patch('revenue.management.commands.kudos_revenue.requests.get')
    def test_command_handle(self, mock_func):
        """Test command kudos revenue."""
        mock_func.side_effect = mocked_requests_get

        Command() \
            .handle([], network='rinkeby', account_address=self.account, start_block=0, end_block=2965443)

        assert DigitalGoodPurchase.objects.all() \
            .filter(receive_address__iexact=self.account, tokenName__iexact='ETH').count() == 2

        assert DigitalGoodPurchase.objects.all() \
            .filter(receive_address__iexact=self.account) \
            .exclude(tokenName='ETH').count() == 0
