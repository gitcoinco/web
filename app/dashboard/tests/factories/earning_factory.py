from django.contrib.contenttypes.models import ContentType

import factory
from dashboard.models import Earning
from grants.tests.factories import GrantFactory


class EarningFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Earning

    value_usd = factory.Faker('pyfloat')
    network = 'mainnet'
    source = factory.SubFactory(GrantFactory)
    source_id = factory.Faker('pyint')
    source_type = factory.LazyAttribute(
        lambda obj: ContentType.objects.get_for_model(obj.source)
    )
