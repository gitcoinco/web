# -*- coding: utf-8 -*-
"""Define the management command to generate EthOS hops.

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
import warnings
from random import randint

from django.core.management.base import BaseCommand

from ethos.models import Hop, ShortCode, TwitterProfile

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


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
    'MiccomServices5',
    'bdosari',
    'knowerlittle',
    'JPasintSHC',
    'savils',
    'elmerm',
    'ILovePythonMore',
    'icoexplorer',
    'HanimMYusof',
    'GWierzowiecki',
    'bohendo',
    'bigc1745',
    'stojce',
    'jeffesquivels',
    'QuikNode',
    'e3amn2l',
    'asinghchrony',
    'hiimmox',
    'c_t_ogden',
    'theycallmeken',
    'Danteintheloop',
    'AugurProject',
    'misterpikul',
    'sincibx',
    'gats8y',
    'scryptomagna',
    'iMichaelTen',
    '_hydeenoble',
    'jhselvik',
    'SUCCULENTS__',
    'SamyakJ04711116',
    'MarkTomsu',
    'freezing_point',
    'dangguillen',
    'rickmanelius',
    'LElkan',
    'cattron313',
    'Beezel_Bug',
    'kevinwucodes',
    'X11Spain',
    'occhiphaura',
    '2GatherUs',
    'jakrabbit',
    'RVNCoin',
    'BertBoeiend',
    'illbeanywhere',
    'adeloveh1',
    'EdgarTwit1',
    'ResetDavid',
    'allkindzzz',
    'planetary_dev',
    'Tom_Wolters',
    'Petru_Catana',
    'i_instances',
    'azeemansar',
    'tomazy',
    'brendanboyle87',
    'jaronrayhinds',
    'matthewholey',
    'kuriyamaPG',
    'evandroguedes',
    'matmeth_',
    'TuanAnh1011',
    'irpansy09096981',
    'MohammedAziz90',
    'live_s_s',
    'gregsantos',
    'CodeManDeluxe',
    'pro_webhosting',
    'randal_olson',
    'lvl_jesse',
    'kristofer_done',
    'breadboardkill',
    'Teo_Blockerz',
    'palash2504',
    'hedgehogy',
    'dredense',
    'kokossmoss',
    'sogasg',
    'artesesan',
    'scsab',
    'jenmacchiarelli',
    'yarrumretep',
    'keithtmccartney',
    'Cryptoscillator',
    'MillerApps',
    '5kyn0d3',
    'Mitch_Kosowski',
    'LamsonScribner',
    'mbeacom',
    'moneyfordogfood',
    'michelgotta',
    'vietlq',
    'Ruski93',
    'Skip_Carlson',
    'jakerockland',
    'NukeManDan',
    'MatthewLilley',
    'tylertommy21',
    'kelvin60429',
    'GetGitcoin',
    'owocki']
# create more with
# followers = api.GetFollowers(count=200)
# [follower.screen_name for follower in followers]


class Command(BaseCommand):
    """Define the management command to generate EthOS Hops."""

    help = 'generates some ethos hops'

    def add_arguments(self, parser):
        """Define the arguments for the command."""
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        """Define the command handling to generate hops."""
        for i in range(0, options['count']):
            shortcode_index = randint(1, ShortCode.objects.count())
            shortcode = ShortCode.objects.get(pk=shortcode_index)
            twitter_profile, _ = TwitterProfile.objects.get_or_create(
                username=twitter_usernames[randint(0, len(twitter_usernames))]
            )
            # username = twitter_usernames[randint(0, len(twitter_usernames))]
            # N = 10
            # username = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
            print(twitter_profile.username)
            # profile_pic = f'https://twitter.com/EthOSEthereal/profile_image?size=original'

            try:
                previous_hop = Hop.objects.filter(shortcode=shortcode).latest('pk')
            except Exception:
                previous_hop = None

            Hop.objects.create(
                twitter_profile=twitter_profile,
                shortcode=shortcode,
                previous_hop=previous_hop,
                ip='127.0.0.1'
            )
            # TODO: Build the graph for each hop.
            # hop.build_graph(latest=False)

            print(f'Hop by {twitter_profile.username} for {shortcode.shortcode}')
