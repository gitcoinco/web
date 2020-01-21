from django.utils import timezone

from grants.models import Contribution, PhantomFunding

start = timezone.datetime(2020, 1, 6)
end = timezone.datetime(2020, 1, 21)

contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True)
pfs = PhantomFunding.objects.filter(created_on__gt=start, created_on__lt=end)
total = contributions.count() + pfs.count()

contributors = len(set(list(contributions.values_list('subscription__contributor_profile', flat=True)) + list(pfs.values_list('profile', flat=True))))
amount = sum([float(contrib.subscription.amount_per_period_usdt) for contrib in contributions] + [float(pf.value) for pf in pfs])

print(total)
print(contributors)
print(amount)
