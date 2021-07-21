'''
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

'''

import time
import uuid

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone

from avatar.models import AvatarTextOverlayInput
from dashboard.utils import get_web3, has_tx_mined
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from web3 import Web3


class Command(BaseCommand):

    help = 'creates avatar text inputs'

    def add_arguments(self, parser):
        parser.add_argument('amount', default='0.001', type=str, help="how much do we send?")
        parser.add_argument('number', type=int, help="how many do we send?")

    def handle(self, *args, **options):
        ## creates text inputs which can be hidden in gitcoin avatars

        # setup
        network = 'mainnet' if not settings.DEBUG else 'rinkeby'
        amount = float(options['amount'])
        amount = int(amount * 10**18)
        number = int(options['number'])
        from_address = settings.AVATAR_ADDRESS
        from_address = Web3.toChecksumAddress(from_address)
        from_pk = settings.AVATAR_PRIVATE_KEY
        w3 = get_web3(network)

        # generate accounts
        accounts = []
        for i in range(0, number):
            entropy = str(uuid.uuid4())
            acct = w3.eth.account.create(entropy)
            accounts.append(acct)

        # generate the accounts and
        # send them to the database
        counter = 1
        for account in accounts:
            try:
                # do the send
                to = account.address
                private_key = account.privateKey
                to = Web3.toChecksumAddress(to)
                txn = {
                    'to': to,
                    'from': from_address,
                    'value': amount,
                    'nonce': w3.eth.getTransactionCount(from_address),
                    'gas': 22000,
                    'gasPrice': int(float(recommend_min_gas_price_to_confirm_in_time(1)) * 10**9 * 1.4),
                    'data': b'',
                }
                signed = w3.eth.account.signTransaction(txn, from_pk)
                tx_id = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

                # wait for it to mine
                print(f"({counter}/{number}) - paid via", tx_id)
                while not has_tx_mined(tx_id, network):
                    time.sleep(1)

                # save to db
                AvatarTextOverlayInput.objects.create(
                    active=True,
                    text=private_key.hex(),
                    coment='auto avatar text creation',
                    num_uses_total=1,
                    current_uses=0,
                    num_uses_remaining=1,
                )
                counter += 1
            except Exception as e:
                print(e)
