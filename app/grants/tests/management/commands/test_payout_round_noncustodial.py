import pytest
from django.core.management import CommandError, call_command
from io import StringIO
from unittest import mock

from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import ContributionFactory, CLRMatchFactory, GrantFactory, SubscriptionFactory

def test_error_message_informs_to_pass_in_network(self):
        error = ''
        try:
            call_command('payout_round_noncustodial', '--contract-address=abc123')
        except CommandError as e:
            import pdb; pdb.set_trace()
            error = str(e)

        assert error == "Error: the following arguments are required: --network/-n"