# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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

"""
from unittest.mock import patch

from marketing.management.commands.remarket_bounties import Command
from test_plus.test import TestCase


class TestRemarketTweet(TestCase):
    """Define tests for remarket tweet."""

    @patch('marketing.management.commands.remarket_bounties.maybe_market_to_twitter')
    def test_handle_no_bounties(self, mock_func):
        """Test command remarket tweet with no bounties."""
        Command().handle()

        assert mock_func.call_count == 0

#TODO: uncomment when remarket_tweet logic will be activated
# @patch('marketing.management.commands.remarket_tweet.maybe_market_to_twitter')
# def test_handle_with_bounties(self, mock_func):
#     """Test command remarket tweet with bounties."""
#     for i in range(3):
#         bounty = Bounty.objects.create(
#             title='foo',
#             value_in_token=3,
#             token_name='USDT',
#             web3_created=datetime(2008, 10, 31),
#             github_url='https://github.com/gitcoinco/web',
#             token_address='0x0',
#             issue_description='hello world',
#             bounty_owner_github_username='flintstone',
#             is_open=True,
#             accepted=True,
#             expires_date=timezone.now() + timedelta(days=1, hours=1),
#             idx_project_length=5,
#             project_length='Months',
#             bounty_type='Feature',
#             experience_level='Intermediate',
#             raw_data={},
#             idx_status='open',
#             bounty_owner_email='john@bar.com',
#             current_bounty=True,
#             network='mainnet'
#         )
#     Command().handle()
#
#     assert mock_func.call_count == 1
