'''
    Copyright (C) 2019 Gitcoin Core

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

'''

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from linkshortener.models import Link


class Command(BaseCommand):

    help = 'generates some links'

    def add_arguments(self, parser):
        parser.add_argument('num', type=int)
        parser.add_argument('comments')

    def handle(self, *args, **options):

        for i in range(0, options['num']):
            link = Link.objects.create(
                shortcode=get_random_string(8),
                url='https://gitcoin.co/',
                comments=options['comments']
                )
            print("https://gitcoin.co/l/" + link.shortcode)
