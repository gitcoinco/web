# -*- coding: utf-8 -*-
"""Handle app url related tests.

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
from secrets import token_hex

from django.urls import resolve, reverse

from test_plus.test import TestCase


class KudosUrlsTestCase(TestCase):
    """Define tests for kudos urls."""

    def setUp(self):
        """Setup the Kudos URL testcase."""
        self.key = token_hex(16)[:29]
        self.tx = 0x0123456789
        self.network = 'rinkeby'

    def test_kudos_main_reverse(self):
        """Test the kudos main url and check the reverse."""
        self.assertEqual(reverse('kudos:main'), '/kudos')

    def test_kudos_main_resolve(self):
        """Test the kudos main url and check the resolution."""
        self.assertEqual(resolve('/kudos').view_name, 'kudos:main')

    def test_kudos_about_reverse(self):
        """Test the kudos about url and check the reverse."""
        self.assertEqual(reverse('kudos:about'), '/kudos/about')

    def test_kudos_about_resolve(self):
        """Test the kudos about url and check the resolution."""
        self.assertEqual(resolve('/kudos/about').view_name, 'kudos:about')

    def test_kudos_marketplace_reverse(self):
        """Test the kudos marketplace url and check the reverse."""
        self.assertEqual(reverse('kudos:marketplace'), '/kudos/marketplace')

    def test_kudos_marketplace_resolve(self):
        """Test the kudos marketplace url and check the resolution."""
        self.assertEqual(resolve('/kudos/marketplace').view_name, 'kudos:marketplace')

    def test_kudos_mint_reverse(self):
        """Test the kudos mint url and check the reverse."""
        self.assertEqual(reverse('kudos:mint'), '/kudos/mint')

    def test_kudos_mint_resolve(self):
        """Test the kudos mint url and check the resolution."""
        self.assertEqual(resolve('/kudos/mint').view_name, 'kudos:mint')

    def test_kudos_send_reverse(self):
        """Test the kudos send url and check the reverse."""
        self.assertEqual(reverse('kudos:send'), '/kudos/send')

    def test_kudos_send_resolve(self):
        """Test the kudos send url and check the resolution."""
        self.assertEqual(resolve('/kudos/send').view_name, 'kudos:send')

    def test_kudos_send_3_reverse(self):
        """Test the kudos send_3 url and check the reverse."""
        self.assertEqual(reverse('kudos:send_3'), '/kudos/send/3')

    def test_kudos_send_3_resolve(self):
        """Test the kudos send_3 url and check the resolution."""
        self.assertEqual(resolve('/kudos/send/3').view_name, 'kudos:send_3')

    def test_kudos_send_4_reverse(self):
        """Test the kudos send_4 url and check the reverse."""
        self.assertEqual(reverse('kudos:send_4'), '/kudos/send/4')

    def test_kudos_send_4_resolve(self):
        """Test the kudos send_4 url and check the resolution."""
        self.assertEqual(resolve('/kudos/send/4').view_name, 'kudos:send_4')

    def test_kudos_receive_reverse(self):
        """Test the kudos receive url and check the reverse."""
        self.assertEqual(
            reverse('kudos:receive', args=(self.key, self.tx, self.network)),
            f'/kudos/receive/v3/{self.key}/{self.tx}/{self.network}'
        )

    def test_kudos_receive_resolve(self):
        """Test the kudos receive url and check the resolution."""
        self.assertEqual(resolve('/kudos/receive/v3/{self.key}/{self.tx}/{self.network}').view_name, 'kudos:receive')

    def test_kudos_receive_bulk_reverse(self):
        """Test the kudos receive bulk url and check the reverse."""
        self.assertEqual(
            reverse('kudos:receive_bulk', args=(self.key, )),
            f'/kudos/redeem/{self.key}'
        )

    def test_kudos_receive_bulk_resolve(self):
        """Test the kudos receive bulk url and check the resolution."""
        self.assertEqual(resolve('/kudos/redeem/{self.key}').view_name, 'kudos:receive_bulk')

    def test_kudos_search_reverse(self):
        """Test the kudos search url and check the reverse."""
        self.assertEqual(reverse('kudos:search'), '/kudos/search/')

    def test_kudos_search_resolve(self):
        """Test the kudos search url and check the resolution."""
        self.assertEqual(resolve('/kudos/search/').view_name, 'kudos:search')

    def test_kudos_details_by_address_token_id_reverse(self):
        """Test the kudos details by address and token id url and check the reverse."""
        self.assertEqual(
            reverse('kudos:details_by_address_and_token_id', args=(self.tx, 1, 'test')),
            f'/kudos/redeem/{self.tx}/1/test'
        )

    def test_kudos_details_by_address_token_id_resolve(self):
        """Test the kudos details by address and token id url and check the resolution."""
        self.assertEqual(resolve('/kudos/redeem/{self.tx}/1/test').view_name, 'kudos:details_by_address_and_token_id')

    def test_kudos_details_reverse(self):
        """Test the kudos details url and check the reverse."""
        self.assertEqual(reverse('kudos:details', args=(1, 'test', )), '/kudos/1/test')

    def test_kudos_details_resolve(self):
        """Test the kudos details url and check the resolution."""
        self.assertEqual(resolve('/kudos/1/test').view_name, 'kudos:details')

    def test_kudos_preferred_wallet_reverse(self):
        """Test the kudos preferred wallet url and check the reverse."""
        self.assertEqual(reverse('kudos:preferred_wallet', args=('test', )), '/kudos/address/test')

    def test_kudos_preferred_wallet_resolve(self):
        """Test the kudos preferred wallet url and check the resolution."""
        self.assertEqual(resolve('/kudos/address/test').view_name, 'kudos:preferred_wallet')
