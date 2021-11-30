import pytest
from grants.models.clr_match import CLRMatch
from grants.models.contribution import Contribution
from grants.models.grant import Grant
from grants.tests.factories import CLRMatchFactory


@pytest.mark.django_db
class TestCLRMatch:
    """Test CLRMatch model."""

    def test_creation(self):
        """Test CLRMatch returned by factory is valid."""

        clr_match = CLRMatchFactory()

        assert isinstance(clr_match, CLRMatch)

    def test_clr_match_has_round_number(self):
        """Test 'round_number' attribute is present."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'round_number')

    def test_clr_match_has_amount(self):
        """Test 'amount' attribute is present and is a float."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'amount')

    def test_clr_match_has_an_associated_grant(self):
        """Test 'grant' attribute is present and is an instance of Grant."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'grant')
        assert isinstance(clr_match.grant, Grant)

    def test_clr_match_has_a_has_passed_kyc_attribute(self):
        """Test 'has_passed_kyc' attribute is present and defaults to False."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'has_passed_kyc')
        assert clr_match.has_passed_kyc == False

    def test_clr_match_has_a_ready_for_test_payout_attribute(self):
        """Test 'ready_for_test_payout' attribute is present and defaults to False."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'ready_for_test_payout')
        assert clr_match.ready_for_test_payout == False

    def test_clr_match_has_a_test_payout_tx(self):
        """Test 'test_payout_tx' attribute is present."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'test_payout_tx')

    def test_clr_match_has_a_test_payout_tx_date(self):
        """Test 'test_payout_tx_date' attribute is present."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'test_payout_tx_date')

    def test_clr_match_has_a_test_payout_contribution(self):
        """Test 'test_payout_contribution' attribute is present and is an instance of Contribution."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'test_payout_contribution')
        assert isinstance(clr_match.test_payout_contribution, Contribution)

    def test_clr_match_has_a_ready_for_payout_attribute(self):
        """Test 'ready_for_payout' attribute is present and defaults to False."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'ready_for_payout')
        assert clr_match.ready_for_payout == False

    def test_clr_match_has_payout_tx(self):
        """Test 'payout_tx' attribute is present."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'payout_tx')

    def test_clr_match_has_payout_tx_date(self):
        """Test 'payout_tx_date' attribute is present."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'payout_tx_date')

    def test_clr_match_has_payout_contribution_attribute(self):
        """Test 'payout_contribution' attribute is present and is an instance of Contribution."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'payout_contribution')
        assert isinstance(clr_match.payout_contribution, Contribution)

    def test_clr_match_has_comments(self):
        """Test 'comments' attribute is present and defaults to empty string."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'comments')
        assert clr_match.comments == ''
