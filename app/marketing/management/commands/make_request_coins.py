# -*- coding: utf-8 -*-
"""Define the GDPR reconsent command for EU users.

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
import time
import warnings
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from linkshortener.models import Link


class Command(BaseCommand):

    help = 'makes a bunch of request coins'

    def handle(self, *args, **options):

        _dict = {
            35: 84,
            50: 84,
            100: 84,
        }

        for denom, count in _dict.items():
            for i in range(0, count):
                comments = f"{denom} Request Coin"
                code = get_random_string(8)
                link = Link.objects.create(
                    shortcode=code,
                    url=f'https://gitcoin.co/requests?code={code}',
                    comments=comments,
                    uses=0,
                    )
                print(f"{comments}, https://gitcoin.co/l/" + link.shortcode)
