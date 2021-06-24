# note: only use this if the admin is failling

import time

from dashboard.utils import has_tx_mined
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from kudos.management.commands.mint_all_kudos import sync_latest
from kudos.models import TokenRequest
from marketing.mails import notify_kudos_minted

change_owner = True

token_req_ids = [
    2465,
    2464,
    2463,
    2462,
    2461,
    2460,
    2459,
]
token_req_ids = TokenRequest.objects.filter(approved=False, rejection_reason='').values_list('pk', flat=True)

for token_req_id in token_req_ids:
    obj = TokenRequest.objects.get(pk=token_req_id)
    multiplier = 1
    gas_price = int(float(recommend_min_gas_price_to_confirm_in_time(1)) * multiplier)
    tx_id = obj.mint(gas_price)
    time.sleep(3)
    notify_kudos_minted(obj)
    obj.approved = True
    if change_owner:
        obj.to_address = '0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F'
    obj.save()
    time.sleep(1)

num_to_sync = 500 + len(token_req_ids)
for i in range(0, num_to_sync):
    sync_latest(i, obj.network)
