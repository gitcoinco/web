from django.utils import timezone

from dashboard.models import Profile
from grants.models import *

gcb = Profile.objects.get(handle='gitcoinbot')
then = timezone.datetime(2020, 9, 14)
grant_pk = 86
contributions = Contribution.objects.filter(subscription__grant__pk=grant_pk, created_on__gt=then)
results = {
    'True': 0, 
    'False': 0, 
}
for contrib in contributions:
    is_automatic = bool(contrib.subscription.amount_per_period == contrib.subscription.gas_price)
    key = str(is_automatic)
    #key = (str(bool(round(contrib.subscription.gas_price,1))))
    results[key] += 1
    if is_automatic:
        contrib.profile_for_clr = gcb
        contrib.match = False
        contrib.save()
print(results)
