# -*- coding: utf-8 -*-
"""Handle github utility related tests.

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
from django.test import TestCase

from dashboard.tokens import addr_to_token, get_tokens


class DashboardTokensTest(TestCase):
    """Define tests for Dashboard tokens module."""

    fixtures = ['tokens.json']

    def test_tokens(self):
        """Test the dashboard tokens variable to ensure it can be read properly."""
        tokens = get_tokens()
        assert isinstance(tokens, list)
        assert isinstance(tokens[0], dict)
        assert len(tokens[0]) == 4

    def test_addr_to_token_valid(self):
        """Test the dashboard token lookup utility with a valid token."""
        token = addr_to_token('0x0000000000000000000000000000000000000000')
        assert isinstance(token, dict)
        assert token['addr'] == '0x0000000000000000000000000000000000000000'
        assert token['name'] == 'ETH'
        assert token['decimals'] == 18

    def test_addr_to_token_invalid(self):
        """Test the dashboard token lookup utility with an invalid token."""
        token = addr_to_token('0xGITCOIN')
        assert isinstance(token, bool)
        assert token is False
