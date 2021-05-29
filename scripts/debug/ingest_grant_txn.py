from django.utils import timezone

import requests
from dashboard.models import Activity, Profile
from economy.tx import headers
from economy.utils import convert_token_to_usdt
from grants.models import Contribution, Grant, Subscription

handle = 'marczeller'
txid = '0xb6e8821954f518164fce7d8601eafc96b5afa1204c49c38691aa21bc4169c1ce'
token = 'ETH'
to_address = '0x9531c059098e3d194ff87febb587ab07b30b1306'
from_address = '0x329c54289ff5d6b7b7dae13592c6b1eda1543ed4'
do_write = True
created_on = timezone.now()
#created_on = timezone.datetime(2020, 6, 15, 8, 0)


profile = Profile.objects.get(handle=handle)

symbol = token
value = 1.68
decimals = 18
value_adjusted = int(value / 10 **int(decimals))
to = to_address
grant = Grant.objects.filter(admin_address__iexact=to).order_by('-positive_round_contributor_count').first()


#ingest data
currency = symbol
amount = value
usd_val = amount * convert_token_to_usdt(symbol)

# convert formats
date = timezone.now()

# create objects
validator_comment = f"created by ingest grant txn script"
subscription = Subscription()
subscription.is_postive_vote = True
subscription.active = False
subscription.error = True
subscription.contributor_address = '/NA'
subscription.amount_per_period = amount
subscription.real_period_seconds = 2592000
subscription.frequency = 30
subscription.frequency_unit = 'N/A'
subscription.token_address = '0x0'
subscription.token_symbol = currency
subscription.gas_price = 0
subscription.new_approve_tx_id = '0x0'
subscription.num_tx_approved = 1
subscription.network = 'mainnet'
subscription.contributor_profile = profile
subscription.grant = grant
subscription.comments = validator_comment
subscription.amount_per_period_usdt = usd_val
subscription.save()
if created_on:
    subscription.created_on = created_on
    subscription.save()

contrib = Contribution.objects.create(
    success=True,
    tx_cleared=True,
    tx_override=True,
    tx_id=txid,
    subscription=subscription,
    validator_passed=True,
    validator_comment=validator_comment,
    )
if created_on:
    contrib.created_on = created_on
    contrib.save()
print(f"ingested {subscription.pk} / {contrib.pk}")

metadata = {
    'id': subscription.id,
    'value_in_token': str(subscription.amount_per_period),
    'value_in_usdt_now': str(round(subscription.amount_per_period_usdt,2)),
    'token_name': subscription.token_symbol,
    'title': subscription.grant.title,
    'grant_url': subscription.grant.url,
    'num_tx_approved': subscription.num_tx_approved,
    'category': 'grant',
}
kwargs = {
    'profile': profile,
    'subscription': subscription,
    'grant': subscription.grant,
    'activity_type': 'new_grant_contribution',
    'metadata': metadata,
}

Activity.objects.create(**kwargs)
