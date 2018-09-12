# -*- coding: utf-8 -*-
"""Handle app utility related tests.

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
from app.utils import func_name
from test_plus.test import TestCase


class AppUrlsTestCase(TestCase):
    """Define tests for app utils."""

    @staticmethod
    def test_func_name():
        """Test the func_name method and ensure parent method matches."""
        function_name = func_name()
        assert function_name == 'test_func_name'
