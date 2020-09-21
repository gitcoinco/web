# for recreating contributions that failed to crate contributions
from django.utils import timezone

from grants.models import *

counter = 0
for subscription in Subscription.objects.filter(created_on__gt=timezone.datetime(2020, 9, 14)):
    if not subscription.subscription_contribution.exists():
        counter += 1
        print(counter, subscription.pk, subscription.token_address, subscription.amount_per_period, subscription.amount_per_period_usdt)
        subscription.successful_contribution(subscription.new_approve_tx_id);
