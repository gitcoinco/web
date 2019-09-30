
from django.utils import timezone

from grants.clr import predict_clr


d1 = timezone.now() - timezone.timedelta(days=12)
d2 = timezone.now()

for i in range((d2 - d1).days * 24 + 1):
    this_date = d1 + timezone.timedelta(hours=i)
    clr_prediction_curves = predict_clr(random_data=False, save_to_db=True, from_date=this_date)

    print(f"finished CLR estimates for {this_date}")
