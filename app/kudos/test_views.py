# -*- coding: utf-8 -*-
"""Test the Kudos Views.

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
import logging
from unittest import skip

from django.test import Client, TestCase

# from .utils import KudosContract

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


class KudosViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_about(self):
        r = self.client.get('/kudos/')
        self.assertEqual(r.status_code, 200)
        r = self.client.get('/kudos/about/')
        self.assertEqual(r.status_code, 200)

    def test_marketplace(self):
        r = self.client.get('/kudos/marketplace/')
        self.assertEqual(r.status_code, 200)

        r = self.client.get('/kudos/marketplace/?q=python')
        self.assertEqual(r.status_code, 200)

    # @skip(reason='stub for future testing')
    # def test_image(self):
    #     self.client.get('/kudos/1')

    # @skip(reason='stub for future testing')
    # def test_details_by_address_and_token_id(self):
    #     c = Client()
    #     c.get('/kudos/1')

    # @skip(reason='stub for future testing')
    # def test_details(self):
    #     self.client.get('/kudos/1')

    def test_mint(self):
        r = self.client.get('/kudos/mint/')
        self.assertEqual(r.status_code, 200)

    # @skip(reason='stub for future testing')
    # def test_get_to_emails(self):
    #     self.client.get('/kudos/1')

    # @skip(reason='stub for future testing')
    # def test_kudos_preferred_wallet(self):
    #     self.client.get('/kudos/1')

    # @skip(reason='stub for future testing')
    # def test_tipee_address(self):
    #     self.client.get('/kudos/1')

    def test_send_2(self):
        r = self.client.get('/kudos/send/')
        self.assertEqual(r.status_code, 302)
        # r = self.client.get('/kudos/send/?id=1')
        # self.assertEqual(r.status_code, 200)

    # @skip(reason='stub for future testing')
    # def test_send_3(self):
    #     self.client.get('/kudos/1')

    # @skip(reason='stub for future testing')
    # def test_send_4(self):
    #     self.client.get('/kudos/1')

    # @skip(reason='stub for future testing')
    # def test_record_kudos_email_activity(self):
    #     pass

    # @skip(reason='stub for future testing')
    # def test_receive(self):
    #     pass
