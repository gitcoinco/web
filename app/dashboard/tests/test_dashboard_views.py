# -*- coding: utf-8 -*-
"""Handle dashboard views related tests.

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

'''
import asyncio
import json
from datetime import date, datetime, timedelta
from unittest import TestCase

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone

import requests
from app.settings import BMAS_ENDPOINT, ES_CORE_ENDPOINT, ES_USER_ENDPOINT
from dashboard.models import Profile
from dashboard.views import verify_user_duniter
from duniterpy.api import bma
from duniterpy.api.client import RESPONSE_AIOHTTP, Client
from duniterpy.documents import BlockUID
from duniterpy.documents.certification import Certification, Identity

CERTIFICATIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "pubkey": {"type": "string"},
        "uid": {"type": "string"},
        "isMember": {"type": "boolean"},
        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pubkey": {"type": "string"},
                    "uid": {"type": "string"},
                    "cert_time": {
                        "type": "object",
                        "properties": {
                            "block": {"type": "number"},
                            "medianTime": {"type": "number"},
                        },
                        "required": ["block", "medianTime"],
                    },
                    "sigDate": {"type": "string"},
                    "written": {
                        "oneOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "number": {"type": "number"},
                                    "hash": {"type": "string"},
                                },
                                "required": ["number", "hash"],
                            },
                            {"type": "null"},
                        ]
                    },
                    "isMember": {"type": "boolean"},
                    "wasMember": {"type": "boolean"},
                    "signature": {"type": "string"},
                },
                "required": [
                    "pubkey",
                    "uid",
                    "cert_time",
                    "sigDate",
                    "written",
                    "wasMember",
                    "isMember",
                    "signature",
                ],
            },
        },
    },
    "required": ["pubkey", "uid", "isMember", "certifications"],
}

def get_certification_document(
    current_block: dict, self_cert_document: Identity, from_pubkey: str
) -> Certification:
    """
    Create and return a Certification document
    :param current_block: Current block data
    :param self_cert_document: Identity document
    :param from_pubkey: Pubkey of the certifier
    :rtype: Certification
    """
    # construct Certification Document
    return Certification(
        version=10,
        currency=current_block["currency"],
        pubkey_from=from_pubkey,
        identity=self_cert_document,
        timestamp=BlockUID(current_block["number"], current_block["hash"]),
        signature="",
    )

class VerifyUserDuniterTests(TestCase):
    async def test_get_search_user_duniter(self):
        client = Client(ES_USER_ENDPOINT)

        gitcoin_handle = "developerfred"
        search_user_duniter_url = await client.get("user/profile/_search?q={0}".format(gitcoin_handle))

        response = requests.get(search_user_duniter_url)

        self.assertTrue(response.ok)


    async def test_get_public_key_duniter(self):
        client = Client(ES_USER_ENDPOINT)
        gitcoin_handle = "developerfred"
        search_user_duniter_url = await client.get("user/profile/_search?q={0}".format(gitcoin_handle))
        pub_res = "9PDu1zkECAKZd5uULKZz6ecAeHuv5FtnzCruhBM4a5cr"

        response = requests.get(search_user_duniter_url)
        duniter_user_response = response.json()
        position = duniter_user_response.get('hits', {}).get('hits', {})
        public_key_duniter = next(iter(position)).get('_id', {})

        self.assertEqual(public_key_duniter, pub_res)

    async def test_same_uid_duniter(self):
        client = Client(BMAS_ENDPOINT)
        gitcoin_handle = "leomatteudi"
        public_key_duniter = "13XfrqY92tTCDbtu2jFAHsgNbZ9Ne2r5Ts1VGhSCrvUb"

        lookup_data = await client(bma.wot.lookup, public_key_duniter)

        response = requests.get(lookup_data)
        duniter_lockup_response = response.json().get('results', {})[0].get('uids', '')[0].get('uid', '')

        self.assertEqual(duniter_lockup_response, gitcoin_handle)

    async def test_is_duniter_member(self):
        client = Client(BMAS_ENDPOINT)
        public_key_duniter = "13XfrqY92tTCDbtu2jFAHsgNbZ9Ne2r5Ts1VGhSCrvUb"
        cert = await get_certification_document(client, public_key_duniter)
        response = requests.get(cert)
        member_data = response.json()
        is_verified = member_data.get('isMember', {})

        self.assertTrue(is_verified)
'''
