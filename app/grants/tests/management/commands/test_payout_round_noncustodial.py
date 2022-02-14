import pytest
from django.core.management import CommandError, call_command
from io import StringIO
from unittest import mock

from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import ContributionFactory, CLRMatchFactory, GrantFactory, SubscriptionFactory

@pytest.mark.django_db
class TestPayoutRoundNoncustodial:
    def test_error_message_informs_to_pass_in_what(self):
            error = ''
            try:
                call_command('payout_round_noncustodial', '--clr_pks=1,2')
            except CommandError as e:
                error = str(e)

            assert error == "Error: the following arguments are required: what"

    def test_error_message_informs_to_pass_in_clr_pks_and_clr_round(self):
            error = ''
            try:
                call_command('payout_round_noncustodial', 'verify')
            except Exception as e:
                error = str(e)

            assert error == "Must provide clr_round and clr_pks"

    def test_error_message_informs_to_pass_in_grant_payout_pk(self):
            error = ''
            try:
                call_command('payout_round_noncustodial', 'verify', '--clr_pks=1,2', '--clr_round=1')
            except Exception as e:
                error = str(e)

            assert error == "Must provide grant_payout_pk containing payout contract info"
    
    def test_error_message_informs_to_pass_valid_what(self):
            error = ''
            try:
                call_command('payout_round_noncustodial', 'verifies_payout', '--clr_pks=1,2', '--clr_round=1')
            except Exception as e:
                error = str(e)

            assert error == "Invalid value verifies_payout for 'what' arg"

    # def test_error_message_informs_to_pass_in_network(self):
    #         error = ''
    #         try:
    #             import pdb; pdb.set_trace()
    #             call_command('payout_round_noncustodial', 'verify')
    #         except CommandError as e:
    #             error = str(e)

    #         assert error == "Exception: Must provide clr_round and clr_pks"