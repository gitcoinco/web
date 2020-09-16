from django.utils import timezone

from dashboard.models import Profile, Tip
from dashboard.tip_views import get_profile

to_username = ''
from_username = ''
token_address = '0x0000000000000000000000000000000000000000'
txid = ''
token_address = ''
from_address = ''
tokenName = ''
amount = 0
created_on = timezone.now()
#created_on = timezone.datetime(2020, 6, 15, 8, 0)
ip='192.168.0.1'

tip = Tip.objects.create(
    primary_email=get_profile(to_username).email,
    emails=[],
    tokenName=tokenName,
    amount=amount,
    comments_priv='',
    comments_public='',
    ip=ip,
    expires_date=created_on,
    github_url='',
    from_name=from_username,
    from_email=get_profile(from_username).email,
    from_username=from_username,
    username=to_username,
    network='mainnet',
    tokenAddress=token_address,
    from_address=from_address,
    is_for_bounty_fulfiller=False,
    metadata={},
    recipient_profile=get_profile(to_username),
    sender_profile=get_profile(from_username),
    txid=txid,
    receive_txid=txid,
    received_on=timezone.now(),
)
print(tip.pk)
