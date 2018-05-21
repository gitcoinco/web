# -*- coding: utf-8 -*-
"""Define the management command to generate EthOS Shortcodes.

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

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from ethos.models import ShortCode


class Command(BaseCommand):
    """Define the management command to generate EthOS shortcodes."""

    help = 'generates some ethos shortcodes'

    def add_arguments(self, parser):
        """Define the arguments for the command."""
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        """Define the command handling to generate shortcodes."""
        short_codes = []
        for i in range(0, options['count']):
            shortcode = get_random_string(8)
            short_codes.append(ShortCode(shortcode=shortcode))
            print(f'https://gitcoin.co/ethos/{shortcode}')

        ShortCode.objects.bulk_create(short_codes)
