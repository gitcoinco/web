import time

from django.db.models import Q

from dashboard.utils import get_web3, has_tx_mined
from kudos.models import KudosTransfer

# pk range to re-send
CAN_OVERRIDE_TO_XDAI = True
TIME_SLEEP = 10
usernames = ['gkobeaga', 'pangelo', 'dmats']

kts = KudosTransfer.objects.filter(username__in=usernames, network='xdai')
print(kts.count())

for kt in kts:
    from kudos.helpers import re_send_kudos_transfer
    txid = re_send_kudos_transfer(kt, CAN_OVERRIDE_TO_XDAI)
    print(kt.username, kt.kudos_token_cloned_from.name, txid)
    time.sleep(TIME_SLEEP)
