import factory
import pytest
from grants.models.flag import Flag

from .grant_factory import GrantFactory
from dashboard.tests.factories import ProfileFactory


@pytest.mark.django_db
class FlagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Flag

    grant = factory.SubFactory(GrantFactory)
    profile = factory.SubFactory(ProfileFactory)
