pk_start = 10731
pk_end = 10775
name_contains = 'devcon_quest_'

################

key_len = 25
i = 0

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.crypto import get_random_string

from dashboard.models import Profile
from kudos.models import BulkTransferCoupon, Token

plaque_kudos = Token.objects.filter(pk__gte=pk_start, pk__lte=pk_end).filter(contract__network='mainnet')

for kudos in plaque_kudos:
    if kudos.gen != 1:
        continue
    num_uses = kudos.num_clones_allowed
    for j in range(0, num_uses):
        _key = get_random_string(key_len)
        btc = BulkTransferCoupon.objects.create(
            token=kudos,
            num_uses_total=1,
            num_uses_remaining=1,
            current_uses=0,
            secret=_key,
            comments_to_put_in_kudos_transfer="Congrats on winning #ETHDenver!",
            sender_profile=Profile.objects.get(handle='gitcoinbot')
            )
        i += 1
        print(f"{j}-{i}, {kudos.humanized_name}, https://gitcoin.co{btc.url}")
