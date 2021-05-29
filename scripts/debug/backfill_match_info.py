from django.db.models import Count
from django.utils import timezone

from grants.models import *
from grants.views import clr_round as round_num


def round_num_to_dates(round_id):
    start = timezone.now()
    end = timezone.now()
    amount = 9
    if round_id == 1:
        start = timezone.datetime(2019, 2, 1)
        end = timezone.datetime(2019, 2, 15)
        amount = 25000
    if round_id == 2:
        start = timezone.datetime(2019, 3, 26)
        end = timezone.datetime(2019, 4, 19)
        amount = 50000
    if round_id == 3:
        start = timezone.datetime(2019, 9, 15)
        end = timezone.datetime(2019, 10, 4)
        amount = 100000
    if round_id == 4:
        start = timezone.datetime(2020, 1, 6)
        end = timezone.datetime(2020, 1, 21)
        amount = 200000
    if round_id == 5:
        start = timezone.datetime(2020, 3, 23)
        end = timezone.datetime(2020, 4, 5)
        amount = 250000
    if round_id == 6:
        start = timezone.datetime(2020, 6, 16)
        end = timezone.datetime(2020, 7, 3)
        amount = 175000
    if round_id == 7:
        start = timezone.datetime(2020, 9, 15)
        end = timezone.datetime(2020, 10, 3)
        amount = 120 * 3 * 1000
    return start, end, amount

for i in range(1, 7):
    skip = GrantCLR.objects.filter(round_num=i).exists()
    if not skip:
        start, end, amount = round_num_to_dates(i)
        GrantCLR.objects.create(
            round_num=i,
            start_date=start,
            end_date=end,
            total_pot=amount,
            )

from_handles = ['owocki', 'vs77bb', 'ceresstation', 'gitcoinbot', 'gitcoingranterog']
for i in range(3, 5):
    start, end, amount = round_num_to_dates(i)
    payout_range = (end, end + timezone.timedelta(weeks=4))
    _contribs = Contribution.objects.filter(created_on__gt=payout_range[0], created_on__lt=payout_range[1])
    contribs = Contribution.objects.filter(subscription__contributor_profile__handle__in=from_handles, created_on__gt=payout_range[0], created_on__lt=payout_range[1])
    for contrib in contribs:
        CLRMatch.objects.create(
            round_number=i,
            amount=contrib.subscription.amount_per_period_usdt,
            grant=contrib.subscription.grant,
            ready_for_payout=True,
            payout_tx=contrib.tx_id,
            payout_tx_date=contrib.created_on,
            payout_contribution=contrib,
            comments='retroactive payout created by backfill_match_info.py'
            )
    #__sum = sum(_contribs.values_list('subscription__amount_per_period_usdt', flat=True))
    #_sum = sum(contribs.values_list('subscription__amount_per_period_usdt', flat=True))
    #print(_contribs.values_list('subscription__contributor_profile__handle').annotate(Count("id")).order_by('-id__count'))
    #print(i, _contribs.count(), contribs.count(), __sum, _sum)

#delete dupes
for i in range(3, 5):
    clrmatches=CLRMatch.objects.filter(round_number=i)
    for grant in Grant.objects.all():
        _clrmatches = clrmatches.filter(grant=grant).order_by('-amount')
        if _clrmatches.count() > 1:
            for clrm in _clrmatches[1:]:
                print(clrm.pk)
                clrm.delete()
