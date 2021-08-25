import pytest
from grants.models.match_pledge import MatchPledge

from .factories.match_pledge_factory import MatchPledgeFactory


@pytest.mark.django_db
class TestMatchPledge:
    """Test MatchPledge model."""

    def test_creation(self):
        """Test instance of MatchPledge returned by factory is valid."""

        match_pledge = MatchPledgeFactory()

        assert isinstance(match_pledge, MatchPledge)

