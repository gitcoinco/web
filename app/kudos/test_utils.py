# -*- coding: utf-8 -*-
"""Test the Kudos utils.

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
import unittest

from django.test import Client, TestCase

from .utils import KudosContract

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)


@unittest.skip(reason='Not creating fresh database and blockchain instances')
class KudosContractTestCase(TestCase):
    def setUp(self):
        self.contract = KudosContract(network='localhost')
        self.metadata = {
            'name': 'pythonista',
            'image': '',
            'description': 'something',
            'external_url': 'http://localhost:8000/kudos',
            'background_color': 'fbfbfb',
            'attributes': []
        }

    def test_mint(self):
        token_uri_url = self.contract.create_token_uri_url(**self.metadata)
        args = (
            '0xD386793F1DB5F21609571C0164841E5eA2D33aD8',
            5,
            1,
            token_uri_url
        )

        self.contract.mint(*args)
