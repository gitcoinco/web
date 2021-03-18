from django.contrib.contenttypes.models import ContentType

from dashboard.models import *
from grants.models import *
from kudos.models import *

for earning in Earning.objects.filter(source_type=ContentType.objects.get(app_label='townsquare', model='matchranking')):
    earning.success = True
    earning.save()

models = [KudosTransfer, Tip, BountyFulfillment, Contribution]
for model in models:
    for obj in model.objects.all():
    	try:
	        print(model, obj.pk)
	        obj.save()
	    except Exception as e:
	    	print(e)
