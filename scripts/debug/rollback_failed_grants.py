# this script was used to handle the subscription billing incident 2019/10/30
# where has_tx-mined incorrectly reported yes and thereby transactions were marked as 
# failures when they werent marked 'succcess' status in the subminer

from django.utils import timezone

from grants.management.commands.subminer import *
from grants.models import Subscription

subs = Subscription.objects.filter(subminer_comments__contains='tx status from RPC is pending not success,')
subs = subs.filter(modified_on__gt=(timezone.now() - timezone.timedelta(hours=48)))
print(subs.count())
for subscription in subs:
    txid = subscription.subminer_comments.split(' ')[9].split("\n")[0]
    print(subscription.pk, txid)
    if txid:
        subscription.active = True
        subscription.error = False
        subscription.successful_contribution(txid)
        subscription.save()
