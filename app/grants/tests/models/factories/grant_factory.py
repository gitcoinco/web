import factory
from grants.models.grant import Grant

from .grant_type_factory import GrantTypeFactory


class GrantFactory(factory.django.DjangoModelFactory):
    """Create mock Grant for testing."""

    class Meta:
        model = Grant

    grant_type = factory.SubFactory(GrantTypeFactory)
