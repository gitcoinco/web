import factory
from grants.models.grant_api_key import GrantAPIKey


class GrantAPIKeyFactory(factory.django.DjangoModelFactory):
    """Create mock GrantAPIKey for testing."""

    class Meta:
        model = GrantAPIKey