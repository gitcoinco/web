import operator

from django.utils import timezone

from grants.models import *
from grants.models import Contribution, PhantomFunding
from grants.views import clr_round, next_round_start, round_end

############################################################################3
# total stats
############################################################################3

start = next_round_start
end = round_end
must_be_successful = True


contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end)
if must_be_successful:
    contributions = contributions.filter(success=True)
pfs = PhantomFunding.objects.filter(created_on__gt=start, created_on__lt=end)
total = contributions.count() + pfs.count()

contributors = len(set(list(contributions.values_list('subscription__contributor_profile', flat=True)) + list(pfs.values_list('profile', flat=True))))
amount = sum([float(contrib.subscription.amount_per_period_usdt) for contrib in contributions] + [float(pf.value) for pf in pfs])

print("contributions", total)
print("contributors", contributors)
print('amount', amount)

############################################################################3
# top contributors
############################################################################3

all_contributors_by_amount = {}
all_contributors_by_num = {}
for contrib in contributions:
    key = contrib.subscription.contributor_profile.handle
    if key not in all_contributors_by_amount.keys():
        all_contributors_by_amount[key] = 0
        all_contributors_by_num[key] = 0

    all_contributors_by_num[key] += 1
    all_contributors_by_amount[key] += contrib.subscription.amount_per_period_usdt

all_contributors_by_num = sorted(all_contributors_by_num.items(), key=operator.itemgetter(1))
all_contributors_by_amount = sorted(all_contributors_by_amount.items(), key=operator.itemgetter(1))
all_contributors_by_num.reverse()
all_contributors_by_amount.reverse()

limit = 50
print(f"Top Contributors by Num Contributions (Round {clr_round})")
counter = 0
for obj in all_contributors_by_num[0:limit]:
    counter += 1
    print(f"{counter} - {str(round(obj[1]))} by {obj[0]}")

print("")
print("=======================")
print("")

counter = 0
print(f"Top Contributors by Amount of Contributions (Round {clr_round})")
for obj in all_contributors_by_amount[0:limit]:
    counter += 1
    print(f"{counter} - ${str(round(obj[1]))} by {obj[0]}")



############################################################################3
# new feature stats for round {clr_round} 
############################################################################3

subs = Subscription.objects.filter(created_on__gt=timezone.now()-timezone.timedelta(hours=48))
subs = subs.filter(subscription_contribution__success=True)
print(subs.count())
print(subs.filter(num_tx_approved__gt=1).count())
print(subs.filter(is_postive_vote=False).count())


############################################################################3
# all contributions export
############################################################################3

start = next_round_start
end = round_end
export = False
if export:
    contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True, subscription__network='mainnet')[0:100]
    print("tx_id1, tx_id2, from address, amount, amount_minus_gitcoin, token_address")
    for contribution in contributions:
        print(contribution.tx_id, 
            contribution.split_tx_id,
            contribution.subscription.contributor_address,
            contribution.subscription.amount_per_period, 
            contribution.subscription.amount_per_period_minus_gas_price,
            contribution.subscription.token_address)
