# -*- coding: utf-8 -*-
"""Handle ENS subdomain utility related tests.

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
from enssubdomain.utils import convert_txn
from test_plus.test import TestCase


class ENSSubdomainUtilsTest(TestCase):
    """Define tests for enssubdomain utilities."""

    @staticmethod
    def test_convert_txn():
        """Test the enssubdomain utility convert_txn."""
        b_txn = b'123456789'
        txn = convert_txn(b_txn)
        assert txn == "0x313233343536373839"
