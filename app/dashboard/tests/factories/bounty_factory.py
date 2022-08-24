from datetime import timedelta

from django.utils import timezone

import factory
from dashboard.models import Bounty


class BountyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bounty
    
    web3_created = factory.LazyFunction(lambda: timezone.now() - timedelta(days=7))
    is_open = factory.Faker('pybool')
    expires_date = factory.LazyFunction(lambda: timezone.now() + timedelta(days=365))
    raw_data = factory.LazyFunction(dict)
    bounty_owner_github_username = factory.LazyFunction(lambda: 'gitcoin')
