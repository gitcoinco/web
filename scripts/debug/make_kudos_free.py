from dashboard.models import Profile
from kudos.models import BulkTransferCoupon

handles = ['xtrullols35', 'sergisi', 'bcaspi', 'gerardguerrero', 'rafacucurull', 'torrestosquella', 'gfelis']
for handle in handles:
    profile = Profile.objects.get(handle__iexact=handle)
    btcs = BulkTransferCoupon.objects.filter(metadata__recipient=profile.pk)
    print(handle, btcs.count())
    for btc in btcs:
        btc.make_paid_for_first_minutes = 0
        btc.save()
