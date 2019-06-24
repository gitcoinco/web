"""Define the change kudos price management command.

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

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.utils import get_nonce, get_web3
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from kudos.models import Token
from kudos.utils import KudosContract

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
formatter = '%(levelname)s:%(name)s.%(funcName)s:%(message)s'


class Command(BaseCommand):

    help = 'changes a bunch of kudos prices by a multiplier of "multiplier"'

    def add_arguments(self, parser):
        parser.add_argument('network', default='localhost', type=str)
        parser.add_argument('multiplier', default='localhost', type=int)
        parser.add_argument('--live', help='whether or not to deploy the proposed changes live', action='store_true')
        parser.add_argument('--filter', default='', type=str, dest='kudos_filter')

    def handle(self, *args, **options):
        # config
        network = options['network']
        _filter = options['kudos_filter']
        live = options['live']
        multiplier = options['multiplier']

        tokens = Token.objects.filter(owner_address=settings.KUDOS_OWNER_ACCOUNT, contract__network=network)
        if _filter:
            tokens = tokens.filter(name__contains=_filter)
        kudos_contract = KudosContract(network=network)._get_contract()
        w3 = get_web3(network)

        for token in tokens:
            if token.gen != 1:
                continue
            print(token)
            if live:
                _tokenId = token.token_id
                _newPriceFinney = token.price_finney * multiplier
                tx = kudos_contract.functions.setPrice(_tokenId, _newPriceFinney).buildTransaction({
                    'nonce': get_nonce(network, settings.KUDOS_OWNER_ACCOUNT),
                    'gas': 47000,
                    'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(5) * 10**9),
                    'value': 0,
                })
                signed = w3.eth.account.signTransaction(tx, settings.KUDOS_PRIVATE_KEY)
                txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
                print(txid)
