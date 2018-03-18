# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from dashboard.models import Tip
from marketing.management.commands.expiration_tip import Command


class TestExpirationTip(TestCase):
    """Define tests for expiration tip."""

    @patch('marketing.management.commands.expiration_tip.tip_email')
    def test_handle(self, mock_func):
        """Test command expiration tip."""
        tip = Tip.objects.create(
            emails=['john@bar.com'],
            tokenName='USDT',
            amount=7,
            username='john',
            network='net',
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            tokenAddress='0x0000000000000000000000000000000000000000'
        )
        Command().handle()

        assert mock_func.call_count == 1

        mock_func.assert_called_once_with(tip, ['john@bar.com'], False)
