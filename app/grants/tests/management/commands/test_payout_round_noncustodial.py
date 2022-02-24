from io import StringIO
from unittest import mock

from django.core.management import CommandError, call_command

import pytest
from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import CLRMatchFactory, GrantFactory, GrantPayoutFactory, GrantCLRFactory, GrantCLRCalculationFactory, GrantTypeFactory
from economy.tests.factories import TokenFactory

prediction_curve=[[0.0, 22051.853262470795, 0.0], [1.0, 22075.114561595507, 23.261299124711513], [10.0, 22112.83567215842, 60.98240968762548], [100.0, 22187.332229392225, 135.47896692142967], [1000.0, 22289.540553690527, 237.6872912197323], [10000.0, 22375.656575359033, 323.803312888238]]
network='mainnet'


@pytest.fixture
def token():
    return TokenFactory(
        address='0x6B175474E89094C44Da98b954EedeAC495271d0F',
        symbol='DAI',
        network=network,
        approved=True
    )


@pytest.fixture
def grant_payout():
    return GrantPayoutFactory(
        contract_address='0xAB8d71d59827dcc90fEDc5DDb97f87eFfB1B1A5B',
        network=network,
        token=token()
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
    return GrantFactory(active=True, network=network, grant_type=grant_type)


@pytest.fixture
def grant_clr_match_factory(grant_payout, grant_factory):
    return CLRMatchFactory(grant=grant_factory, grant_payout=grant_payout, round_number=13)

@pytest.fixture
def user_input_no():
    return 'n'

@pytest.fixture
def user_input_yes():
    return 'y'


@pytest.mark.django_db
class TestPayoutRoundNoncustodialFinalize:
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


    def test_finalize_sums_owed_matches(self, grant_payout, grant_clr_factory, grant_factory, grant_clr_match_factory, user_input_no):
        out = StringIO()

        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input_no
            call_command(
                'payout_round_noncustodial',
                'finalize', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out)

        result = out.getvalue()
        assert f'got 1 grants' in result

    def test_prints_correct_finalize_and_existing_amounts(self, grant_payout, grant_clr_factory, grant_clr_match_factory, grant_factory, user_input_no):
        GrantCLRCalculationFactory(
            grant=grant_factory,
            clr_prediction_curve=prediction_curve,
            grantclr=grant_clr_factory,
            latest=True
        )
        clr_match = CLRMatchFactory(grant=grant_factory, grant_payout=grant_payout, round_number=13)
        out = StringIO()

        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input_no
            call_command(
                'payout_round_noncustodial',
                'finalize', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out
            )

        result = out.getvalue()
        scheduled_matches = [clr_match, grant_clr_match_factory]
        total = sum(sm.amount for sm in scheduled_matches)

        assert f'there are 1 grants to finalize worth ${round((prediction_curve[0][1]), 2)}' in result
        assert f'there are {len(scheduled_matches)} Match Payments already created worth ${round(total, 2)}' in result

    def test_if_clr_match_is_created_when_no_payout_is_zeros(self, grant_payout, grant_clr_factory, grant_clr_match_factory, user_input_yes, grant_type):
        grant = GrantFactory(active=True, network='mainnet', grant_type=grant_type)
        GrantCLRCalculationFactory(
            grant=grant,
            clr_prediction_curve=[[0, 0]],
            grantclr=grant_clr_factory,
            latest=True
        )

        out = StringIO()
        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input_yes
            call_command(
                'payout_round_noncustodial',
                'finalize', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out
            )
        result = out.getvalue()
        assert f'0 matches were created' in result

    def test_that_clr_match_is_created(self, grant_payout, grant_clr_factory, grant_clr_match_factory, user_input_yes, grant_type):
        profile = ProfileFactory()
        grant = GrantFactory(active=True, network='mainnet', grant_type=grant_type, admin_profile=profile)
        GrantCLRCalculationFactory(
            grant=grant,
            clr_prediction_curve=prediction_curve,
            grantclr=grant_clr_factory,
            latest=True
        )

        out = StringIO()
        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input_yes
            call_command(
                'payout_round_noncustodial',
                'finalize', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out
            )
        result = out.getvalue()
        assert f'1 matches were created' in result

@pytest.mark.django_db
class TestPayoutRoundNoncustodialFinalPayout:
    def test_payout_warnings_showscorrect_count(self, grant_type, grant_clr_factory, grant_payout, grant_clr_match_factory, user_input_yes):
        profile = ProfileFactory()
        grant = GrantFactory(active=True, network='mainnet', grant_type=grant_type, admin_profile=profile)
        GrantCLRCalculationFactory(
            grant=grant,
            clr_prediction_curve=prediction_curve,
            grantclr=grant_clr_factory,
            latest=True
        )

        out = StringIO()
        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input_yes
            call_command(
                'payout_round_noncustodial',
                'prepare_final_payout', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out
            )

        result = out.getvalue()
        amount = round(grant_clr_match_factory.amount, 2)

        assert f'there are 1 UNPAID Match Payments already created worth {amount} DAI ( AKA ${amount} ) on {network}' in result
        assert f'promoted' in result

@pytest.mark.django_db
class TestPayoutRoundNoncustodialSetPayouts:
    def test_setpayouts_initial_colelctions_are_correct(self, grant_type, grant_clr_factory, grant_clr_match_factory, grant_payout, user_input_yes, grant_factory):
        grant = GrantFactory(active=True, network='mainnet', grant_type=grant_type)
        GrantCLRCalculationFactory(
            grant=grant,
            clr_prediction_curve=prediction_curve,
            grantclr=grant_clr_factory,
            latest=True
        )

        paid_match = CLRMatchFactory(
            grant=grant_factory,
            grant_payout=grant_payout,
            round_number=13,
            ready_for_payout=True,
            payout_tx='0x8bb02920638514c809c8bfc62ba7e7b8f619fae89ff02c4e9ba955191b9a7176'
        )
        
        unpaid_pending_kyc = CLRMatchFactory(
            grant=grant_factory,
            grant_payout=grant_payout,
            round_number=13,
            ready_for_payout=False
        )

        unpaid_no_kyc = CLRMatchFactory(
            grant=grant_factory,
            grant_payout=grant_payout,
            round_number=13,
            ready_for_payout=True,
            payout_tx=''
        )

        out = StringIO()
        with mock.patch('grants.management.commands.payout_round_noncustodial.input') as input:
            input.return_value = user_input_yes
            call_command(
                'payout_round_noncustodial',
                'set_payouts', 
                f'--clr_pks={grant_clr_factory.pk}',
                f'--clr_round={grant_clr_match_factory.round_number}',
                f'--grant_payout_pk={grant_payout.pk}',
                stdout=out)

        result = out.getvalue()

        unpaid = [unpaid_no_kyc, unpaid_pending_kyc, grant_clr_match_factory]
        unpaid_ready = [unpaid_no_kyc, unpaid_pending_kyc, grant_clr_match_factory]

        total_paid_matches = round(paid_match.amount,2)
        total_owed_matches = round(sum(sm.amount for sm in unpaid), 2)
        total_pending_kyc_matches = round(sum(sm.amount for sm in [unpaid_pending_kyc, grant_clr_match_factory]), 2)
        total_no_kyc_matches = round(sum(sm.amount for sm in unpaid_ready),2)

        assert f"there are 1 PAID Match (MADE MANUALLY/ALREADY UPLOADED) {total_paid_matches} DAI ( AKA ${total_paid_matches} ) on {network}" in result
        assert f"there are {len(unpaid)} UNPAID Match Payments worth {total_owed_matches} DAI ( AKA ${total_owed_matches} ) on {network} of which: " in result
        assert f"------> {len([unpaid_pending_kyc, grant_clr_match_factory])} UNPAID Matches PENDING KYC ${total_pending_kyc_matches} DAI ( AKA ${total_pending_kyc_matches} )" in result
        assert f"------> {len(unpaid_ready)} UNPAID Matches SKIPPING KYC {total_no_kyc_matches} DAI ( AKA ${total_no_kyc_matches} )"