import pytest
from dashboard.models import Profile
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

    def test_match_pledge_belongs_to_profile(self):
        """Test relation to Profile."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'profile')
        assert isinstance(match_pledge.profile, Profile)

    def test_match_pledge_has_amount_attribute(self):
        """Test 'amount' attribute and default value."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'amount')
        assert match_pledge.amount == 1

    def test_match_pledge_has_pledge_type_attribute(self):
        """Test 'pledge_type' attribute."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'pledge_type')
        assert match_pledge.pledge_type == None

    def test_match_pledge_has_comments(self):
        """Test 'comments' attribute and default value."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'comments')
        assert match_pledge.comments == ''
