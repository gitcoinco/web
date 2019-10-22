name_contains = 'devcon_quest_'
num_uses = 1000
num_qr_codes_to_create_per_kudos = 1

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.crypto import get_random_string

from dashboard.models import Profile
from kudos.models import BulkTransferCoupon, Token

plaque_kudos = Token.objects.filter(Q(name__contains=name_contains)).filter(contract__network='mainnet')

if do_create_airdrop_links_for_sponsors:
    for kudos in plaque_kudos:
        for i in range(0, num_qr_codes_to_create_per_kudos):
            _key = get_random_string(key_len)
            btc = BulkTransferCoupon.objects.create(
                token=kudos,
                num_uses_total=num_uses,
                num_uses_remaining=num_uses,
                current_uses=0,
                secret=_key,
                comments_to_put_in_kudos_transfer="Congrats on winning #ETHDenver2019!",
                sender_profile=Profile.objects.get(handle='gitcoinbot')
                )
            print(f"{i}, {kudos.humanized_name}, {btc.url}")
