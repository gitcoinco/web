from datetime import datetime, timedelta

import factory
from dashboard.models import Bounty


class BountyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bounty

    web3_created = datetime.now()
    is_open = True
    expires_date = datetime.now() + timedelta(days=365)
    raw_data = {}
    
