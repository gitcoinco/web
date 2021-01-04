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
import time
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Profile
from dashboard.utils import get_web3
from web3 import Web3
from django.conf import settings
from django.utils import timezone

from dashboard.models import Profile, Tip
from dashboard.tip_views import get_profile

class Command(BaseCommand):

    help = 'send tips according to whats in a google spreadsheet'


    def handle(self, *args, **options):
        # setup
        data = b'Happy Holidays.  Hope you have a 1337 one! ~ Team Gitcoin'
        network = 'mainnet'
        from_address = settings.TIP_PAYOUT_ADDRESS
        from_pk = settings.TIP_PAYOUT_PRIVATE_KEY
        from_username = 'gitcoinbot'
        w3 = get_web3(network)
        AMOUNT = int(1.337 * 10**18)
        SLEEP_TIME = 30
        DEBUG_GAS_PRICE = 311 * 10**9
        filename = 'Gitcoin Holiday Survey (Responses) - Form Responses 1.csv'
        with open(filename, 'r', newline='', encoding='utf_8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                email = row['Email Address']
                addr = row['What is your PERSONAL (not gitcoin) ETH address?']
                print(email, addr)
                profile = Profile.objects.filter(email=email).first()
                if not profile:
                    profile = Profile.objects.get(handle='gitcoinbot')
                print(profile)
                gasPrice = DEBUG_GAS_PRICE
                #gasPrice = int(float(recommend_min_gas_price_to_confirm_in_time(1)) * 10**9 * 1.4) if not settings.DEBUG else DEBUG_GAS_PRICE
                private_key = from_pk
                to = Web3.toChecksumAddress(addr)
                txn = {
                    'to': to,
                    'from': from_address,
                    'value': AMOUNT,
                    'nonce': w3.eth.getTransactionCount(from_address),
                    'gas': 22000,
                    'gasPrice': gasPrice,
                    'data': data,
                }
                signed = w3.eth.account.signTransaction(txn, from_pk)
                tx_id = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
                print(tx_id)



                to_username = profile.handle
                from_username = 'gitcoinbot'
                token_address = '0x0000000000000000000000000000000000000000'
                txid = tx_id
                token_address = ''
                from_address = from_address
                tokenName = 'ETH'
                amount = AMOUNT / 10**18
                created_on = timezone.now()
                #created_on = timezone.datetime(2020, 6, 15, 8, 0)
                ip='192.168.0.1'

                tip = Tip.objects.create(
                    primary_email=get_profile(to_username).email,
                    emails=[],
                    tokenName=tokenName,
                    amount=amount,
                    comments_priv=f'Holiday 2020 Tip from Gitcoin to {email}',
                    comments_public='',
                    ip=ip,
                    expires_date=created_on,
                    github_url='',
                    from_name=from_username,
                    from_email=get_profile(from_username).email,
                    from_username=from_username,
                    username=to_username,
                    network='mainnet',
                    tokenAddress=token_address,
                    from_address=from_address,
                    is_for_bounty_fulfiller=False,
                    metadata={},
                    recipient_profile=get_profile(to_username),
                    sender_profile=get_profile(from_username),
                    txid=txid,
                    receive_txid=txid,
                    received_on=timezone.now(),
                )
                print(tip.pk)

                print('-')
                time.sleep(SLEEP_TIME)
                print('-')

        