import pytest
from grants.models.subscription import Subscription

from .factories.subscription_factory import SubscriptionFactory


@pytest.mark.django_db
class TestSubscription:
    """Test Subscription model."""

    def test_creation(self):
        """Test instance of Subscription returned by factory is valid."""

        subscription = SubscriptionFactory()

        assert isinstance(subscription, Subscription)

    def test_subscription_has_active_attribute(self):
        """Test 'active' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'active')
        assert subscription.active == True

    def test_subscription_has_error_attribute(self):
        """Terror 'error' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'error')
        assert subscription.error == False
    