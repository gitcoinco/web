import factory
from grants.models.subscription import Subscription


class SubscriptionFactory(factory.django.DjangoModelFactory):
    """Create mock Subscription for testing."""

    class Meta:
        model = Subscription