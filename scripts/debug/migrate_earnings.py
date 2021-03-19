from django.contrib.contenttypes.models import ContentType

from dashboard.models import *
from grants.models import *
from kudos.models import *

sums = {}

for earning in Earning.objects.filter(source_type=ContentType.objects.get(app_label='townsquare', model='matchranking')):
    earning.success = True
    earning.save()

models = [Contribution Tip, BountyFulfillment,KudosTransfer,]
for model in models:
	sum[str(model)] = 0
    for obj in model.objects.all():
        try:
            print(model, obj.pk)
            obj.save()
			sum[str(model)] = += obj.value_in_usdt_then
        except Exception as e:
            print(e)

