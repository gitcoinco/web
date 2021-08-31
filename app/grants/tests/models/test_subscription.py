from django.utils import timezone

import pytest
from dashboard.models import Profile
from grants.models.grant import Grant
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

    def test_subscription_has_token_address(self):
        """Test token_address attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'token_address')
        assert subscription.token_address == '0x0'

    def test_subscription_has_token_symbol(self):
        """Test token_symbol attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'token_symbol')
        assert subscription.token_symbol == '0x0'

    def test_subscription_has_gas_price(self):
        """Test gas_price attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'gas_price')
        assert subscription.gas_price == 1

    def test_subscription_has_new_approve_tx_id_attribute(self):
        """Test new_approve_tx_id attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'new_approve_tx_id')
        assert subscription.new_approve_tx_id == '0x0'

    def test_subscription_has_end_approve_tx_id_attribute(self):
        """Test end_approve_tx_id attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'end_approve_tx_id')
        assert subscription.end_approve_tx_id == '0x0'

    def test_subscription_has_cancel_tx_id_attribute(self):
        """Test cancel_tx_id attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'cancel_tx_id')
        assert subscription.cancel_tx_id == '0x0'

    def test_subscription_has_num_tx_approved_attribute(self):
        """Test num_tx_approved attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'num_tx_approved')
        assert subscription.num_tx_approved == 1

    def test_subscription_has_num_tx_processed_attribute(self):
        """Test num_tx_processed attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'num_tx_processed')
        assert subscription.num_tx_processed == 0

    def test_subscription_has_network(self):
        """Test network attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'network')
        assert subscription.network == 'mainnet'

    def test_subscription_has_associated_grant(self):
        """Test association with Grant."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, "grant")
        assert isinstance(subscription.grant, Grant)

    def test_subscription_has_associated_profile(self):
        """Test Subscription contributor's Profile attribute."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'contributor_profile')
        assert isinstance(subscription.contributor_profile, Profile)

    def test_subscription_has_last_contribution_date(self):
        """Test last_contribution_date attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'last_contribution_date')
        assert subscription.last_contribution_date == timezone.datetime(1990, 1, 1)

    def test_subscription_has_next_contribution_date(self):
        """Test next_contribution_date attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'next_contribution_date')
        assert subscription.next_contribution_date == timezone.datetime(1990, 1, 1)

    def test_subscription_has_amount_per_period_usdt_attribute(self):
        """Test amount_per_period_usdt attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'amount_per_period_usdt')
        assert subscription.amount_per_period_usdt == 0
        
    def test_subscription_has_tenant(self):
        """Test tenant attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'tenant')
        assert subscription.tenant == "ETH"

    def test_subscription_has_a_visitor_id(self):
        """Test visitorId attribute and default value."""

        subscription = SubscriptionFactory()

        assert hasattr(subscription, 'visitorId')
        assert subscription.visitorId == ''

