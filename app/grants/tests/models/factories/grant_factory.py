import factory
from grants.models.grant import Grant


class GrantFactory(factory.django.DjangoModelFactory):
    """Create mock Grant for testing."""

    class Meta:
        model = Grant
