from grants.models import *
from django.utils import timezone
start = timezone.now() - timezone.timedelta(hours=24)
contributions = Contribution.objects.filter(created_on__gt=start).order_by('-created_on')
contributions = contributions.filter(validator_comment__icontains='is_correct_recipient')
contributions = contributions[:10]
for contrib in contributions:
    print(contrib.pk)
    contrib.update_tx_status()


