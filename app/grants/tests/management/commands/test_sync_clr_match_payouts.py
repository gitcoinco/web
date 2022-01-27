from io import StringIO
from unittest import mock

from django.core.management import CommandError, call_command

import pytest
from grants.tests.factories import CLRMatchFactory, GrantFactory, GrantPayoutFactory


@pytest.fixture
def grant_payout():
    return GrantPayoutFactory(
        contract_address='0xAB8d71d59827dcc90fEDc5DDb97f87eFfB1B1A5B',
        network='mainnet'
    )


@pytest.fixture
def payout_logs():
    return [
        {
            'recipient': '0x230fc981f7cae90cfc4ed4c18f7c178b239e5f9f',
            'tx_hash': '0x8b5def65058838c52a72efb48b62b251eb8c5e91334fbc65a3b9bd4b5f0182d1',
        }
    ]


@pytest.mark.django_db
class TestSyncCLRMatchPayouts:
    def test_error_message_informs_to_pass_in_network(self):
        error = ''
        try:
            call_command('sync_clr_match_payouts', '--contract-address=abc123')
        except CommandError as e:
            error = str(e)

        assert error == "Error: the following arguments are required: --network/-n"

    def test_error_message_informs_to_pass_in_contract_address(self):
        error = ''
        try:
            call_command('sync_clr_match_payouts', '--network=mainnet')
        except CommandError as e:
            error = str(e)

        assert error == "Error: the following arguments are required: --contract-address/-c"

    def test_reports_number_of_clr_matches_missing_claim_tx(self, grant_payout):
        grant = GrantFactory(admin_address='0x230fc981f7cae90cfc4ed4c18f7c178b239e5f9f')

        CLRMatchFactory(grant=grant, grant_payout=grant_payout)

        out = StringIO()
        call_command(
            'sync_clr_match_payouts',
            f'-n {grant_payout.network}',
            f'-c {grant_payout.contract_address}',
            stdout=out
        )

        result = out.getvalue()
        assert "Number of unclaimed CLR Matches: 1" in result

    def test_reports_each_item_being_updated(self, grant_payout, payout_logs):
        grant = GrantFactory(admin_address='0x230fc981f7cae90cfc4ed4c18f7c178b239e5f9f')
        match = CLRMatchFactory(
            grant=grant,
            grant_payout=grant_payout,
            amount=2.0,
            round_number=12
        )

        out = StringIO()
        with mock.patch('grants.management.commands.sync_clr_match_payouts.MatchesContract.get_payout_claimed_entries') as events:
            events.return_value = payout_logs
            call_command(
                'sync_clr_match_payouts',
                f'-n {grant_payout.network}',
                f'-c {grant_payout.contract_address}',
                stdout=out
            )

        result = out.getvalue()
        assert f"Updating CLR Match - {match.pk}" in result

    def test_reports_total_updates(self, grant_payout, payout_logs):
        grant = GrantFactory(admin_address='0x230fc981f7cae90cfc4ed4c18f7c178b239e5f9f')
        CLRMatchFactory(
            grant=grant,
            grant_payout=grant_payout,
            amount=2.0,
            round_number=12
        )

        out = StringIO()

        with mock.patch('grants.management.commands.sync_clr_match_payouts.MatchesContract.get_payout_claimed_entries') as events:
            events.return_value = payout_logs
            call_command(
                'sync_clr_match_payouts',
                f'-n {grant_payout.network}',
                f'-c {grant_payout.contract_address}',
                stdout=out
            )

        result = out.getvalue()
        assert f"Total CLR Matches updated 1" in result

    def test_skips_updating_clr_matches_with_existing_claim_tx(self, grant_payout, payout_logs):
        grant = GrantFactory(admin_address='0x230fc981f7cae90cfc4ed4c18f7c178b239e5f9f')
        CLRMatchFactory(
            grant=grant,
            grant_payout=grant_payout,
            amount=2.0,
            round_number=12
        )

        grant = GrantFactory(admin_address='0x230fc981f7cae90cfc4ed4c18f7c178b239e5f9f')
        CLRMatchFactory(
            grant=grant,
            grant_payout=grant_payout,
            amount=2.0,
            round_number=12,
            claim_tx='0x8b5def65058838c52a72efb48b62b251eb8c5e91334fbc65a3b9bd4b5f0182d1'
        )

        out = StringIO()
        with mock.patch('grants.management.commands.sync_clr_match_payouts.MatchesContract.get_payout_claimed_entries') as events:
            events.return_value = payout_logs
            call_command(
                'sync_clr_match_payouts',
                f'-n {grant_payout.network}',
                f'-c {grant_payout.contract_address}',
                stdout=out
            )

        result = out.getvalue()
        assert f"Total CLR Matches updated 1" in result

    def test_catches_value_error_on_new_deploys(self, grant_payout):
        grant = GrantFactory(admin_address='0x230fc981f7cae90cfc4ed4c18f7c178b239e5f9f')
        CLRMatchFactory(grant=grant, grant_payout=grant_payout)

        out = StringIO()

        call_command(
            'sync_clr_match_payouts',
            f'-n {grant_payout.network}',
            f'-c {grant_payout.contract_address}',
            stdout=out
        )

        assert out.getvalue()
