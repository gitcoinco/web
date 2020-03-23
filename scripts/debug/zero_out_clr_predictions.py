from grants.models import Grant
from decimal import Decimal

for grant in Grant.objects.all():
    print(grant.clr_prediction_curve)
    grant.clr_prediction_curve = [0 for i in range(0, 6)]
    print(grant.clr_prediction_curve)
    grant.save()

