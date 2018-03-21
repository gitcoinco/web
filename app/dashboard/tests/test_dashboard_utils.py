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
from dashboard.utils import get_web3
from test_plus.test import TestCase
from web3.main import Web3
from web3.providers.rpc import HTTPProvider


class DashboardUtilsTestCase(TestCase):
    """Define tests for dashboard utils."""

    def test_get_web3(self):
        """Test the dashboard utility get_web3."""
        networks = ['mainnet', 'rinkeby', 'ropsten']
        for network in networks:
            web3_provider = get_web3(network)
            assert isinstance(web3_provider, Web3)
            assert len(web3_provider.providers) == 1
            assert isinstance(web3_provider.providers[0], HTTPProvider)
            assert web3_provider.providers[0].endpoint_uri == f'https://{network}.infura.io'
