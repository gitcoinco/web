import factory
import pytest
from grants.models.grant_api_key import GrantAPIKey


@pytest.mark.django_db
class GrantAPIKeyFactory(factory.django.DjangoModelFactory):
    """Create a mock GrantAPIKey for testing."""

    class Meta:
        model = GrantAPIKey