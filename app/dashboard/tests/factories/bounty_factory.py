from datetime import datetime, timedelta

import factory
from dashboard.models import Bounty


class BountyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bounty

    web3_created = factory.LazyFunction(datetime.now)
    is_open = factory.Faker('pybool')
    expires_date = factory.LazyFunction(lambda: datetime.now() + timedelta(days=365))
    raw_data = factory.LazyFunction(dict)
    bounty_owner_github_username = factory.LazyFunction(lambda: 'gitcoin')
