import pytest
from grants.models.clr_match import CLRMatch
from grants.models.grant import Grant

from .factories.clr_match_factory import CLRMatchFactory


@pytest.mark.django_db
class TestCLRMatch:
    """Test CLRMatch model."""

    def test_creation(self):
        """Test CLRMatch returned by factory is valid."""

        clr_match = CLRMatchFactory()

        assert isinstance(clr_match, CLRMatch)

    def test_clr_match_has_round_number(self):
        """Test 'round_number' attribute and default value."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'round_number')
        assert clr_match.round_number == None

    def test_clr_match_has_amount(self):
        """Test 'amount' attribute and default value."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'amount')
        assert clr_match.amount == 0.0

    def test_clr_match_belongs_to_grant(self):
        """Test CLRMatch has an associated grant."""

        clr_match = CLRMatchFactory()

        assert hasattr(clr_match, 'grant')
        assert isinstance(clr_match.grant, Grant)
