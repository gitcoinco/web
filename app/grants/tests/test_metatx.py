from unittest.mock import MagicMock

from grants.management.commands import subminer
from grants.management.commands.subminer import process_subscription
from grants.models import Grant, Subscription
from test_plus.test import TestCase


class MetatxTest(TestCase):

    def setUp(self):
        self.monthly_subscription = Subscription(real_period_seconds=31*24*60*60,
                                                 network="test",
                                                 grant=Grant())
        self.monthly_subscription.get_subscription_hash_arguments = lambda: {'periodSeconds': self.monthly_subscription.real_period_seconds,
                                                                             'gasPrice': 0}

        self.daily_subscription_free = Subscription(real_period_seconds=24*60*60,
                                                    network="test",
                                                    grant=Grant())
        self.daily_subscription_free.get_subscription_hash_arguments = lambda: {'periodSeconds': self.daily_subscription_free.real_period_seconds,
                                                                                'gasPrice': 0}

        self.daily_subscription_paid = Subscription(real_period_seconds=24*60*60,
                                                    network="test",
                                                    grant=Grant())
        self.daily_subscription_paid.get_subscription_hash_arguments = lambda: {'periodSeconds': self.daily_subscription_paid.real_period_seconds,
                                                                                'gasPrice': 1000000}

        subscriptions = [self.monthly_subscription, self.daily_subscription_free, self.daily_subscription_paid]
        for s in subscriptions:
            s.get_are_we_past_next_valid_timestamp = lambda: True
            s.get_is_subscription_ready_from_web3 = lambda: True
            s.get_is_active_from_web3 = lambda: True
            s.get_subscription_signer_from_web3 = lambda: 'asdfasdf'
            s.is_ready_to_be_processed_web3 = lambda: True
        subminer.has_tx_mined = MagicMock(return_value=True)


    def test_slow_contributions_are_free(self):
        process_subscription(self.monthly_subscription, live=False)
        assert self.monthly_subscription.error is False

    def test_fast_contributions_are_not_free(self):
        try:
            process_subscription(self.daily_subscription_free, live=False)
        except:
            pass
        assert self.daily_subscription_free.error is True

    def test_fast_contributions_cost_gas(self):
        process_subscription(self.daily_subscription_paid, live=False)
        assert self.daily_subscription_paid.error is False
