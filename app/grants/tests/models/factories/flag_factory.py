import factory
import pytest
from grants.models.flag import Flag

from .grant_factory import GrantFactory
from .profile_factory import ProfileFactory


@pytest.mark.django_db
class FlagFactory(factory.django.DjangoModelFactory):
    """Create a mock Flag for testing."""

    class Meta:
        model = Flag

    grant = factory.SubFactory(GrantFactory)
    profile = factory.SubFactory(ProfileFactory)
    comments = ''
