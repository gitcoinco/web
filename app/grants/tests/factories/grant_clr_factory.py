from datetime import datetime, timedelta
from random import choice

import factory
import pytest
from dashboard.tests.factories import ProfileFactory
from grants.models.grant import GrantCLR


@pytest.mark.django_db
class GrantCLRFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantCLR

    round_num = factory.Faker('pyint')
    start_date = factory.LazyFunction(datetime.now)
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(weeks=2))
    type = factory.LazyFunction(lambda: choice(GrantCLR.CLR_TYPES)[0])
    banner_text = factory.Faker('text', max_nb_chars=50)
    owner = factory.SubFactory(ProfileFactory)
