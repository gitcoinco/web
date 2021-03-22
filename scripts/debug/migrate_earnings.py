from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from dashboard.models import *
from grants.models import *
from kudos.models import *

sums = {}
write = True

for earning in Earning.objects.filter(source_type=ContentType.objects.get(app_label='townsquare', model='matchranking')):
    if write:
        earning.success = True
        earning.save()

models = [Contribution, Tip, BountyFulfillment,KudosTransfer,]
for model in models:
    key = str(model)
    sums[key] = 0
    for obj in model.objects.all():
        try:
            if write:
                print(model, obj.pk)
                if obj.modified_on > timezone.now() - timezone.timedelta(hours=6):
                    continue
                obj.save()
            sums[key] += obj.value_in_usdt_then
        except Exception as e:
            print(e)

for key, item in sums.items():
    print(f"{key}: {item}")
