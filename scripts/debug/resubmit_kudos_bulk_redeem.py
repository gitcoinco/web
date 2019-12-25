#https://twitter.com/anettrolikova/status/1145038336140161024?s=12 

from dashboard.models import Profile
from kudos.models import BulkTransferCoupon
from kudos.views import redeem_bulk_coupon

handle = 'AnettRolikova'
secret = 'evil_genius_bot_2019'
address = None

ip_address = '0.0.0.0'
profile = Profile.objects.get(handle=handle)
coupon = BulkTransferCoupon.objects.get(secret=secret)
address = profile.preferred_payout_address
if not address:
    raise Exception("need preferred_payout_address")

success, error, kudos_transfer = redeem_bulk_coupon(coupon, profile, address, ip_address, save_addr=False)

print(success)
print(kudos_transfer.txid)
