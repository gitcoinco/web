import time

from django.db.models import Q

from dashboard.utils import get_web3, has_tx_mined
from kudos.models import KudosTransfer

# pk range to re-send
CAN_OVERRIDE_TO_XDAI = True
min_pk = 1684
max_pk = 1740
TIME_SLEEP = 1
usernames = ['elm87an', 'resgar', 'adnfx2']

kts = KudosTransfer.objects.filter(pk__gte=min_pk, pk__lte=max_pk)
kts = KudosTransfer.objects.filter(username__in=usernames).filter(Q(tx_status='dropped') | Q(txid='pending_celery'))
print(kts.count())

for kt in kts:
    from kudos.helpers import re_send_kudos_transfer
    txid = re_send_kudos_transfer(kt, CAN_OVERRIDE_TO_XDAI)
    while not has_tx_mined(txid, kt.network):
        time.sleep(TIME_SLEEP)
