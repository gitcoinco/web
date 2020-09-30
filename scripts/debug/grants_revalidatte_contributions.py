from django.utils import timezone

from grants.models import *

search_str = 'Expecting value:' #alethio issue
search_str = 'tuple index out of range' #unknown
search_str = 'zkSync' #zksync issue
num_to_process = 100

start = timezone.now() - timezone.timedelta(hours=24)
contributions = Contribution.objects.filter(created_on__gt=start).order_by('-created_on')
contributions = contributions.filter(validator_comment__icontains=search_str)
contributions = contributions[:num_to_process]
for contrib in contributions:
    print(contrib.pk)
    contrib.update_tx_status()
    contrib.save()
