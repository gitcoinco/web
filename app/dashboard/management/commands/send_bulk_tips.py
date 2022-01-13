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

import json
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.abi import erc20_abi as abi
from dashboard.models import Profile, Tip, TipPayout
from dashboard.notifications import maybe_market_tip_to_email, maybe_market_tip_to_github, maybe_market_tip_to_slack
from dashboard.tip_views import record_tip_activity
from dashboard.utils import get_web3, has_tx_mined
from dashboard.views import record_user_action
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from perftools.models import JSONStore
from web3 import Web3

WAIT_TIME_BETWEEN_PAYOUTS = 15

class Command(BaseCommand):

    help = 'finalizes + sends grants round payouts'

    def add_arguments(self, parser):
        parser.add_argument('from_name', 
            default='from_name',
            type=str,
            help="from_username, eg: owocki"
            )
        parser.add_argument('usernames', 
            default='usernames',
            type=str,
            help="list of usernames to pay, a la: user1,user2,user3"
            )

        parser.add_argument('amount', 
            default='amount',
            type=float,
            help="amount of DAI to send, a la: 0.001"
            )

        parser.add_argument('comments_priv', 
            default='comments_priv',
            type=str,
            help="private comments"
            )

        parser.add_argument('comments_public', 
            default='comments_public',
            type=str,
            help="public comments"
            )


    def handle(self, *args, **options):

        network = 'mainnet' if not settings.DEBUG else 'rinkeby'
        actually_send = not settings.DEBUG
        usernames = options['usernames'].split(",")
        _amount = options['amount']
        DECIMALS = 18
        from_address = settings.TIP_PAYOUT_ADDRESS
        from_pk = settings.TIP_PAYOUT_PRIVATE_KEY
        from_username = options['from_name']
        DAI_ADDRESS = '0x6b175474e89094c44da98b954eedeac495271d0f' if network=='mainnet' else '0x6a6e8b58dee0ca4b4ee147ad72d3ddd2ef1bf6f7'
        token_name = 'DAI'
        # https://gitcoin.co/_administrationperftools/jsonstore/1801078/change/
        sybil_attack_addresses = JSONStore.objects.get(key='sybil_attack_addresses').data

        # payout rankings (round must be finalized first)
        TOKEN_ADDRESS = DAI_ADDRESS

        from_profile = Profile.objects.filter(handle=from_username.lower()).first()

        if not from_profile:
            print('no from_profile found')
            return

        sent_addresses = []
        for username in usernames:

            # issue payment
            print(f"- issuing payout to {username}")

            profile = Profile.objects.filter(handle=username.lower()).first()

            if not profile:
                print('no profile found')
                continue
                
            if not profile.preferred_payout_address:
                print('no profile preferred_payout_address found')
                continue
                
            address = profile.preferred_payout_address

            w3 = get_web3(network)
            contract = w3.eth.contract(Web3.toChecksumAddress(TOKEN_ADDRESS), abi=abi)
            address = Web3.toChecksumAddress(address)

            amount = int(_amount * 10**DECIMALS)
            tx_id = '0x0'
            if actually_send:

                if address.lower() in sent_addresses:
                    print('address was already in the sent addresess; skipping due to anti-sybil protections')
                    continue

                if address.lower() in sybil_attack_addresses:
                    print('skipping due to anti-sybil protections')
                    continue

                sent_addresses.append(address.lower())

                tx = contract.functions.transfer(address, amount).buildTransaction({
                    'nonce': w3.eth.getTransactionCount(from_address),
                    'gas': 60000,
                    'gasPrice': int(float(recommend_min_gas_price_to_confirm_in_time(1)) * 10**9 * 1.4)
                })

                signed = w3.eth.account.signTransaction(tx, from_pk)
                tx_id = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

                if not tx_id:
                    print("cannot pay, did not get a txid")
                    continue

                print("paid via", tx_id)

                # wait for tx to clear
                while not has_tx_mined(tx_id, network):
                    time.sleep(1)

            metadata = {
                'direct_address': profile.preferred_payout_address,
                'creation_time': timezone.now().strftime("%Y-%m-%dT%H:00:00"),
            }

            # create objects
            tip = Tip.objects.create(
                primary_email=profile.email,
                emails=[profile.email],
                tokenName='DAI',
                amount=amount/10**DECIMALS,
                comments_priv=options['comments_priv'],
                comments_public=options['comments_public'],
                ip="0.0.0.0",
                expires_date=timezone.now() + timezone.timedelta(days=10),
                github_url='',
                from_name=from_username,
                from_email=from_profile.email,
                from_username=from_username,
                username=profile.handle,
                network=network,
                tokenAddress=TOKEN_ADDRESS,
                from_address=from_address,
                is_for_bounty_fulfiller=False,
                metadata=metadata,
                recipient_profile=profile,
                sender_profile=from_profile,
                tx_status='pending',
                txid=tx_id,
                receive_tx_status='pending',
                receive_txid=tx_id,
                receive_address=profile.preferred_payout_address,
                tx_time=timezone.now(),
                receive_tx_time=timezone.now(),
                received_on=timezone.now(),
            )
            tip.trigger_townsquare()
            maybe_market_tip_to_github(tip)
            maybe_market_tip_to_slack(tip, 'New tip')
            if tip.primary_email:
                maybe_market_tip_to_email(tip, [tip.primary_email])
            record_user_action(tip.from_username, 'send_tip', tip)
            record_tip_activity(tip, tip.from_username, 'new_tip' if tip.username else 'new_crowdfund', False, tip.username)
            TipPayout.objects.create(
                txid=tx_id,
                profile=profile,
                tip=tip,
                )


            print("SLEEPING")
            time.sleep(WAIT_TIME_BETWEEN_PAYOUTS)
            print("DONE SLEEPING")
