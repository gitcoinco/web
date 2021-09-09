import factory
from grants.models.contribution import Contribution


class ContributionFactory(factory.django.DjangoModelFactory):
    """Create mock Contribution for testing."""

    class Meta:
        model = Contribution