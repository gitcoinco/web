import factory
from grants.models.grant_stat import GrantStat

from .grant_factory import GrantFactory


class GrantStatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantStat

    grant = factory.SubFactory(GrantFactory)
