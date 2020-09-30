# use this if grants/stats looks like 
# broken teeth  https://bits.owocki.com/eDuPzdez


from django.utils import timezone

from grants.models import Grant
from marketing.models import Stat

lt_pk = 47067421 * 999

key_titles = [
    ('_match', 'Estimated Matching Amount ($)', '-positive_round_contributor_count', 'grants' ),
    ('_pctrbs', 'Positive Contributors', '-positive_round_contributor_count', 'grants' ),
    ('_nctrbs', 'Negative Contributors', '-negative_round_contributor_count', 'grants' ),
    ('_amt', 'CrowdFund Amount', '-amount_received_in_round', 'grants' ),
    ('_admt1', 'Estimated Matching Amount (in cents) / Twitter Followers', '-positive_round_contributor_count', 'grants' ),
]
keys = [ele[0] for ele in key_titles]

key_list = []
for key in keys:
    top_grants = Grant.objects.filter(active=True)
    grants_keys = [grant.title[0:43] for grant in top_grants]
    for grants_key in grants_keys:
        item = f"{grants_key}{key}"
        key_list.append(item)

print(len(key_list), stats.count())

_from = timezone.now() - timezone.timedelta(days=30)
stats = Stat.objects.filter(key__in=key_list, pk__lt=lt_pk, created_on__gt=_from).order_by('-pk')
for stat in stats:
    stat.created_on -= timezone.timedelta(microseconds=stat.created_on.microsecond)
    stat.created_on -= timezone.timedelta(seconds=int(stat.created_on.strftime('%S')))
    stat.created_on -= timezone.timedelta(minutes=int(stat.created_on.strftime('%M')))
    stat.save()
    print(stat.pk)
