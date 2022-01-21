from io import StringIO

import pytest

from django.core.management import call_command, CommandError

from grants.tests.factories import GrantFactory, GrantPayoutFactory, CLRMatchFactory


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

    def test_reports_number_of_clr_matches_missing_claim_tx(self):
        grant = GrantFactory(admin_address='0xB81C935D01e734b3D8bb233F5c4E1D72DBC30f6c')
        grant_payout = GrantPayoutFactory(
            contract_address='0x0EbD2E2130b73107d0C45fF2E16c93E7e2e10e3a',
            network='mainnet'
        )
        CLRMatchFactory(grant=grant, grant_payout=grant_payout)

        out = StringIO()
        call_command(
            'sync_clr_match_payouts',
            '-n mainnet',
            '-c 0x0EbD2E2130b73107d0C45fF2E16c93E7e2e10e3a',
            stdout=out
        )

        result = out.getvalue()
        assert "Number of unclaimed CLR Matches: 1" in result


