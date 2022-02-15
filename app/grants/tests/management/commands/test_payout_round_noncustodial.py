import pytest
from django.core.management import CommandError, call_command
from io import StringIO
from unittest import mock

from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import ContributionFactory, CLRMatchFactory, GrantFactory, SubscriptionFactory, GrantPayoutFactory, GrantCLRFactory, GrantCLRCalculationFactory, GrantTypeFactory

prediction_curve=[[0.0, 22051.853262470795, 0.0], [1.0, 22075.114561595507, 23.261299124711513], [10.0, 22112.83567215842, 60.98240968762548], [100.0, 22187.332229392225, 135.47896692142967], [1000.0, 22289.540553690527, 237.6872912197323], [10000.0, 22375.656575359033, 323.803312888238]]

@pytest.fixture
def grant_payout():
    return GrantPayoutFactory(
        contract_address='0xAB8d71d59827dcc90fEDc5DDb97f87eFfB1B1A5B',
        network='mainnet'
    )

@pytest.fixture
def grant_type():
    return GrantTypeFactory()

@pytest.fixture
def grant_clr_factory(grant_type):
    return GrantCLRFactory(
        round_num=13,
        grant_filters={"grant_type__in": [grant_type.pk]}
    )

@pytest.fixture
def grant_factory(grant_type):
    return GrantFactory(active=True, network='mainnet', grant_type=grant_type)


@pytest.fixture
def grant_clr_match_factory(grant_payout, grant_factory):
    return CLRMatchFactory(grant=grant_factory, grant_payout=grant_payout, round_number=13)

@pytest.fixture
def yes_continue():
    return 'y'

@pytest.fixture
def user_input():
    return 'y'


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


    def test_finalize_sums_owed_matches(self, grant_payout, grant_clr_factory, grant_factory, grant_clr_match_factory, user_input):
        out = StringIO()

        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input
            call_command(
                'payout_round_noncustodial',
                'finalize', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out)

        result = out.getvalue()
        assert f'got 1 grants' in result


    def test_prints_correct_finalize_and_existing_amounts(self, grant_payout, grant_clr_factory, grant_clr_match_factory, grant_factory, yes_continue):
        GrantCLRCalculationFactory(
            grant=grant_factory,
            clr_prediction_curve=prediction_curve,
            grantclr=grant_clr_factory,
            latest=True
        )
        clr_match = CLRMatchFactory(grant=grant_factory, grant_payout=grant_payout, round_number=13)
        GrantCLRCalculationFactory(
            grant=grant_factory,
            clr_prediction_curve=prediction_curve,
            grantclr=grant_clr_factory,
            latest=True
        )
        out = StringIO()

        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input
            call_command(
                'payout_round_noncustodial',
                'finalize', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out)

        result = out.getvalue()
        scheduled_matches = [clr_match, grant_clr_match_factory]
        total = sum(sm.amount for sm in scheduled_matches)

        assert f'there are 1 grants to finalize worth ${round((prediction_curve[0][1] * 2), 2)}' in result
        assert f'there are {len(scheduled_matches)} Match Payments already created worth ${round(total, 2)}' in result


    # def test_tif_clr_match_is_created_when_no_amount_exists(self, grant_payout, grant_clr_factory, grant_clr_match_factory, grant_factory, yes_continue):
