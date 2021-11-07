from datetime import datetime, timedelta
from random import choice

import factory
import pytest
from grants.models.grant import GrantCLR

from dashboard.tests.factories import ProfileFactory


@pytest.mark.django_db
class GrantCLRFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantCLR

    round_num = factory.Faker('pyint')
    start_date = factory.LazyFunction(datetime.now)
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(weeks=2))
    is_active = factory.Faker('pybool')
    type = factory.LazyFunction(lambda: choice(GrantCLR.CLR_TYPES)[0])
    banner_text = factory.Faker('catch_phrase')
    owner = factory.SubFactory(ProfileFactory)
