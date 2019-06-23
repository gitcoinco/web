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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.crypto import get_random_string

from dashboard.models import Profile
from kudos.models import BulkTransferCoupon, Token


class Command(BaseCommand):

    help = 'bootstraps the kudos data on the platform'

    def handle(self, *args, **options):

        #config 
        do_enable_kudos = True
        do_create_airdrop_links_for_winners = True
        do_create_airdrop_links_for_sponsors = True
        num_qr_codes_to_create = 1000
        key_len = 12

        trophy_kudos = Token.objects.filter(name__contains='ethdenver_winner', contract__network='mainnet')
        plaque_kudos = Token.objects.filter(Q(name__contains='_ethdenver_2019') | Q(name__contains='be_a_bufficorn')).filter(contract__network='mainnet')
        all_kudos = plaque_kudos | trophy_kudos

        # print(f"got {trophy_kudos.count()} trophies")
        # print(f"got {plaque_kudos.count()} plaques")

        if do_enable_kudos:
            for kudos in plaque_kudos:
                kudos.created_on = timezone.now()
                kudos.hidden = False
                kudos.send_enabled_for_non_gitcoin_admins = False
                kudos.save()

        kudos_name_to_num_airdrop_links = {}

        for obj in all_kudos:
            kudos_name_to_num_airdrop_links[obj.name] = 1
        kudos_name_to_num_airdrop_links['ethdenver_winner_runner_up'] = 10
        kudos_name_to_num_airdrop_links['ethdenver_winner_impact_track_finalist'] = 5
        kudos_name_to_num_airdrop_links['ethdenver_winner_open_track_finalist'] = 5

        if do_create_airdrop_links_for_winners:
            for name, val in kudos_name_to_num_airdrop_links.items():
                for i in range(0, val):
                    _key = get_random_string(key_len)
                    btc = BulkTransferCoupon.objects.create(
                        token=Token.objects.filter(name=name).first(),
                        num_uses_total=1,
                        num_uses_remaining=1,
                        current_uses=0,
                        secret=_key,
                        comments_to_put_in_kudos_transfer="Congrats on winning #ETHDenver2019!",
                        sender_profile=Profile.objects.get(handle='gitcoinbot')
                        )
                    print(f"{btc.pk}, {name}, https://gitcoin.co/ethdenver/redeem/{_key}")

        if do_create_airdrop_links_for_sponsors:
            for kudos in plaque_kudos:
                for i in range(0, num_qr_codes_to_create):
                    _key = get_random_string(key_len)
                    btc = BulkTransferCoupon.objects.create(
                        token=kudos,
                        num_uses_total=1,
                        num_uses_remaining=1,
                        current_uses=0,
                        secret=_key,
                        comments_to_put_in_kudos_transfer="Congrats on winning #ETHDenver2019!",
                        sender_profile=Profile.objects.get(handle='gitcoinbot')
                        )
                    print(f"{i}, {kudos.humanized_name}, https://gitcoin.co/ethdenver/redeem/{_key}")
