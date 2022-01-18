from io import StringIO

import pytest

from django.core.management import call_command, CommandError


@pytest.mark.django_db
class TestSyncCLRMatchPayouts:
    def test_exits_with_non_zero_status_when_missing_network(self):
        with pytest.raises(CommandError):
            call_command('sync_clr_match_payouts')

    def test_error_message_informs_to_pass_in_network(self):
        try:
            call_command('sync_clr_match_payouts')
        except CommandError as e:
            assert str(e) == "Error: the following arguments are required: --network/-n"

