token_req_id = 314

from kudos.management.commands.mint_all_kudos import sync_latest
from kudos.models import TokenRequest
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from dashboard.utils import has_tx_mined
import time
from marketing.mails import notify_kudos_minted

obj = TokenRequest.objects.get(pk=token_req_id)
multiplier = 1
gas_price = int(float(recommend_min_gas_price_to_confirm_in_time(1)) * multiplier)
tx_id = obj.mint(gas_price)
while not has_tx_mined(tx_id, obj.network):
    time.sleep(1)
sync_latest(0)
sync_latest(1)
sync_latest(2)
sync_latest(3)
notify_kudos_minted(obj)
