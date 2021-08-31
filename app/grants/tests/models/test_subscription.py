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

    def test_subscription_has_subscription_hash_attribute(self):
        """Test 'subscription_hash' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'subscription_hash')
        assert subscription.subscription_hash == ''

    def test_subscription_has_a_contributor_signature(self):
        """Test 'contributor_signature' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'contributor_signature')
        assert subscription.contributor_signature == ''

    def test_subscription_has_a_contributor_address(self):
        """Test 'contributor_address' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'contributor_address')
        assert subscription.contributor_address == ''

    def test_subscription_has_amount_per_period_attribute(self):
        """Test 'amount_per_period' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'amount_per_period')
        assert subscription.amount_per_period == 1

    def test_subscription_has_real_period_seconds_attribute(self):
        """Test 'real_period_seconds' attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'real_period_seconds')
        assert subscription.real_period_seconds == 2592000

    def test_subscription_has_frequency_unit(self):
        """Test frequency_unit attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'frequency_unit')
        assert subscription.frequency_unit == ''

    def test_subscription_has_frequency_attribute(self):
        """Test frequency attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'frequency')
        assert subscription.frequency == 0

        