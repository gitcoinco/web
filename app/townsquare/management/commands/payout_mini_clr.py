'''
    Copyright (C) 2020 Gitcoin Core

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
from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.utils import get_tx_status, get_web3, has_tx_mined
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from townsquare.models import MatchRound
from web3 import HTTPProvider, Web3

abi = json.loads('[{"constant":true,"inputs":[],"name":"mintingFinished","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_amount","type":"uint256"}],"name":"mint","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_subtractedValue","type":"uint256"}],"name":"decreaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"finishMinting","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_addedValue","type":"uint256"}],"name":"increaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"payable":false,"stateMutability":"nonpayable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"amount","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[],"name":"MintFinished","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]')

class Command(BaseCommand):

    help = 'creates round rankings'

    def handle(self, *args, **options):
        # setup
        minutes_ago = 10 if not settings.DEBUG else 40
        payment_threshold_usd = 1
        network = 'mainnet' if not settings.DEBUG else 'rinkeby'
        from_address = settings.MINICLR_ADDRESS
        from_pk = settings.MINICLR_PRIVATE_KEY
        DAI_ADDRESS = '0x6b175474e89094c44da98b954eedeac495271d0f' if network=='mainnet' else '0x8f2e097e79b1c51be9cba42658862f0192c3e487'
        provider = settings.WEB3_HTTP_PROVIDER if network == 'mainnet' else "https://rinkeby.infura.io/"

        # find a round that has recently expired
        cursor_time = timezone.now() - timezone.timedelta(minutes=minutes_ago)
        mr = MatchRound.objects.filter(valid_from__lt=cursor_time, valid_to__gt=cursor_time, valid_to__lt=timezone.now()).first()
        if not mr:
            print(f'No Match Round Found that ended between {cursor_time} <> {timezone.now()}')
            return
        print(mr)

        # finalize rankings
        rankings = mr.ranking.filter(final=False, paid=False).order_by('number')
        print(rankings.count())
        for ranking in rankings:
            ranking.final = True
            ranking.save()

        # payout rankings
        rankings = mr.ranking.filter(final=True, paid=False).order_by('number')
        print(rankings.count())
        w3 = Web3(HTTPProvider(provider))
        for ranking in rankings:
            print(ranking)

            # figure out amount_owed
            profile = ranking.profile
            owed_rankings = profile.match_rankings.filter(final=True, paid=False)
            amount_owed = sum(owed_rankings.values_list('match_total', flat=True))

            # validate
            error = None
            if amount_owed < payment_threshold_usd:
                error = ("- less than amount owed; continue")
            address = profile.preferred_payout_address
            if not address:
                error = ("- address not on file")

            if error:
                ranking.payout_tx_status = error
                ranking.save()
                continue

            # issue payment
            contract = w3.eth.contract(Web3.toChecksumAddress(DAI_ADDRESS), abi=abi)
            address = Web3.toChecksumAddress(address)
            amount = int(amount_owed * 10**18)
            tx = contract.functions.transfer(address, amount).buildTransaction({
                'nonce': w3.eth.getTransactionCount(from_address),
                'gas': 100000,
                'gasPrice': recommend_min_gas_price_to_confirm_in_time(1) * 10**9
            })

            signed = w3.eth.account.signTransaction(tx, from_pk)
            tx_id = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

            # wait for tx to clear
            while not has_tx_mined(tx_id, network):
                time.sleep(1)

            ranking.payout_tx_status, ranking.payout_tx_issued = get_tx_status(tx_id, network, timezone.now())

            ranking.paid = True
            ranking.payout_txid = tx_id
            ranking.save()
            for other_ranking in owed_rankings:
                other_ranking.paid = True
                other_ranking.payout_txid = ranking.payout_txid
                other_ranking.payout_tx_issued = ranking.payout_tx_issued
                other_ranking.payout_tx_status = ranking.payout_tx_status
                other_ranking.save()
