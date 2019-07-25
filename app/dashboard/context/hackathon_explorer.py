# -*- coding: utf-8 -*-
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

from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

eth_hack = {
    'hackathon_id'  : 'eth_hack',
    'sponsors_gold' : [
        {
            'name'  : 'Quorum',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/quorum.svg')
        },
        {
            'name'  : 'Consensys Labs',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/labs-logo-blue.svg')
        },
        {
            'name'  : 'MythX',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/mythx-light.png')
        },
        {
            'name'  : 'Pegasys',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/pegasys-logo.svg')
        },
        {
            'name'  : 'Microsoft',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/microsoft.svg')
        },
        {
            'name'  : 'Adex',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/adex-vector-logo.svg')
        }
    ],
    'sponsors_silver' : [
        {
            'name'  : 'Chainlink',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/chainlink-hexagon.svg')
        },
        {
            'name'  : 'Kauri',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/kauri_logo_vertical.svg')
        },
        {
            'name'  : 'LeapDAO',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/leapdao.svg')
        },
        {
            'name'  : 'Kleros',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/kleros-logo-vertical.svg')
        },
        {
            'name'  : 'Alethio',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/alethio-no-bg.svg')
        },
        {
            'name'  : 'Coinmark',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/coinmark_blue_lg.svg')
        },
        {
            'name'  : 'Autom(8)',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/autom8.svg')
        },
        {
            'name'  : 'POA',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/logo_poa.svg')
        }
    ]
}

beyondblockchain_2019 = {
    'sponsor_bg'    : 'none',
    'sponsors_gold' : [
        {
            'name'  : 'Raiden',
            'logo'  : static('v2/images/hackathon/beyond_block/sponsors/raiden-white.svg')
        },
        {
            'name'  : 'Consensys Labs',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/labs-logo-blue.svg')
        },
        {
            'name'  : 'Pegasys',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/big/pegasys-logo.svg')
        },
        {
            'name'  : 'Portis',
            'logo'  : static('v2/images/hackathon/beyond_block/sponsors/portis.svg')
        },
    ],
    'sponsors_silver' : [
        {
            'name'  : 'Alethio',
            'logo'  : static('v2/images/hackathon/ethhack/sponsors/small/alethio-white.svg')
        },
        {
            'name'  : 'TheGraph',
            'logo'  : static('v2/images/hackathon/beyond_block/sponsors/thegraph-white.svg')
        },
        {
            'name'  : 'Arweave',
            'logo'  : static('v2/images/hackathon/beyond_block/sponsors/arweave-white.svg')
        },
    ],
}
