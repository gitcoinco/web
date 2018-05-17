# -*- coding: utf-8 -*-
"""Handle dashboard utility related tests.

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
from dashboard.utils import (
    get_bounty, get_bounty_id_from_db, get_bounty_id_from_web3, get_ordinal_repr, get_web3, getBountyContract,
)
from test_plus.test import TestCase
from web3.main import Web3
from web3.providers.rpc import HTTPProvider


class DashboardUtilsTest(TestCase):
    """Define tests for dashboard utils."""

    @staticmethod
    def test_get_web3():
        """Test the dashboard utility get_web3."""
        networks = ['mainnet', 'rinkeby', 'ropsten']
        for network in networks:
            web3_provider = get_web3(network)
            assert isinstance(web3_provider, Web3)
            assert len(web3_provider.providers) == 1
            assert isinstance(web3_provider.providers[0], HTTPProvider)
            assert web3_provider.providers[0].endpoint_uri == f'https://{network}.infura.io'

    @staticmethod
    def test_get_bounty_contract():
        assert getBountyContract('mainnet').address == "0x2af47a65da8CD66729b4209C22017d6A5C2d2400"

    @staticmethod
    def test_get_bounty():
        assert get_bounty(100, 'mainnet')['contract_deadline'] == 1522802516

    @staticmethod
    def test_get_bounty_id_from_db():
        """ There should be no bounty with this id in the db"""
        assert not get_bounty_id_from_db('https://github.com/gitcoinco/web/issues/607', 'mainnet')

    @staticmethod
    def test_get_bounty_id_from_web3():
        # find bounty 249
        assert get_bounty_id_from_web3('https://github.com/raiden-network/raiden/issues/1195', 'mainnet', 246) == 249
        assert not get_bounty_id_from_web3('https://github.com/gitcoinco/web/issues/607', 'mainnet', 10000000)

    @staticmethod
    def test_get_ordinal_repr():
        """Test the dashboard utility get_ordinal_repr."""
        assert get_ordinal_repr(1) == '1st'
        assert get_ordinal_repr(2) == '2nd'
        assert get_ordinal_repr(3) == '3rd'
        assert get_ordinal_repr(4) == '4th'
        assert get_ordinal_repr(10) == '10th'
        assert get_ordinal_repr(11) == '11th'
        assert get_ordinal_repr(21) == '21st'
        assert get_ordinal_repr(22) == '22nd'
        assert get_ordinal_repr(23) == '23rd'
        assert get_ordinal_repr(24) == '24th'
