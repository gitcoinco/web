import factory
from grants.models.grant_type import GrantType


class GrantTypeFactory(factory.django.DjangoModelFactory):
    """Create mock GrantType for testing."""

    class Meta:
        model = GrantType

