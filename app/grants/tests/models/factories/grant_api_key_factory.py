import factory
import pytest
from dashboard.tests.factories.profile_factory import ProfileFactory
from grants.models.grant_api_key import GrantAPIKey


@pytest.mark.django_db
class GrantAPIKeyFactory(factory.django.DjangoModelFactory):
    """Create a mock GrantAPIKey for testing."""

    class Meta:
        model = GrantAPIKey

    profile = factory.SubFactory(ProfileFactory)
