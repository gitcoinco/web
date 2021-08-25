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

    def test_match_pledge_has_active_attribute(self):
        """Test 'active' attribute and default value."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'active')
        assert match_pledge.active == False

    def test_match_pledge_has_profile_attribute(self):
        """Test 'profile' attribute and default value."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'profile')
        assert match_pledge.profile == None