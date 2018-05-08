'''
    Copyright (C) 2017 Gitcoin Core

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

from random import randint

from django.core.management.base import BaseCommand

from ethos.models import Hop, ShortCode

twitter_usernames = [
    'eswara_sai',
    'owocki',
    'mbeacom',
    'mitch_kosowski',
    'vishesh04',
    'abhiram383',
    'EthOS_ERC20',
    'thelostone_mc',
    'rajat100493',
    'vsinghdothings'
]


class Command(BaseCommand):
    help = 'generates some ethos hops'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        for i in range(0, options['count']):
            shortcode_index = randint(1, ShortCode.objects.count())
            shortcode = ShortCode.objects.get(pk=shortcode_index)
            username = twitter_usernames[randint(0, 9)]
            profile_pic = f'https://twitter.com/{username}/profile_image?size=original'

            if i % 10 != 0:
                previous_hop = Hop.objects.latest('pk')
            else:
                previous_hop = None

            Hop.objects.create(
                twitter_username=username,
                twitter_profile_pic=profile_pic,
                shortcode=shortcode,
                previous_hop=previous_hop,
                ip='127.0.0.1'
            )

            print(f'Hop by {username} for {shortcode.shortcode}')
