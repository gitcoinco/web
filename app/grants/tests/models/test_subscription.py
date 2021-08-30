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
        """Test 'error' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'error')
        assert subscription.error == False
    
    def test_subscription_has_subminer_comments(self):
        """Test 'subminer_comments' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'subminer_comments')
        assert subscription.subminer_comments == ''

    def test_subscription_has_comments(self):
        """Test 'comments' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'comments')
        assert subscription.comments == ''

    def test_subscription_has_split_tx_id(self):
        """Test 'split_tx_id' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'split_tx_id')
        assert subscription.split_tx_id == ''

    def test_subscription_has_is_postive_vote_attribute(self):
        """Test 'is_postive_vote' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'is_postive_vote')
        assert subscription.is_postive_vote == True

    def test_subscription_has_split_tx_confirmed_attribute(self):
        """Test 'split_tx_confirmed' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'split_tx_confirmed')
        assert subscription.split_tx_confirmed == False