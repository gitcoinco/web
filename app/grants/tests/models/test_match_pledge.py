from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.timezone import localtime

import pytest
from dashboard.models import Profile
from grants.models.grant import GrantCLR
from grants.models.match_pledge import MatchPledge

from grants.tests.factories import MatchPledgeFactory


@pytest.mark.django_db
class TestMatchPledge:
    """Test MatchPledge model."""

    def test_creation(self):
        """Test instance of MatchPledge returned by factory is valid."""

        match_pledge = MatchPledgeFactory()

        assert isinstance(match_pledge, MatchPledge)

    def test_match_pledge_has_active_attribute(self):
        """Test 'active' attribute is present and defaults to False."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'active')
        assert match_pledge.active == False

    def test_match_pledge_has_associated_profile(self):
        """Test 'profile' attribute is present and is an instance of Profile."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'profile')
        assert isinstance(match_pledge.profile, Profile)

    def test_match_pledge_has_amount_attribute(self):
        """Test 'amount' attribute is present defaults to 1."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'amount')
        assert match_pledge.amount == 1

    def test_match_pledge_has_pledge_type_attribute(self):
        """Test 'pledge_type' attribute is present."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'pledge_type')

    def test_match_pledge_has_comments(self):
        """Test 'comments' attribute is present and defaults to empty string."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'comments')
        assert match_pledge.comments == ''

    def test_match_pledge_has_end_date(self):
        """Test 'end_date' attribute is present and that default value is 30 days from today's date."""

        next_month = localtime(timezone.now() + timedelta(days=30))
        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'end_date')
        assert isinstance(match_pledge.end_date, datetime)
        assert match_pledge.end_date.replace(microsecond=0) == next_month.replace(microsecond=0)

    def test_match_pledge_has_data_attribute(self):
        """Test 'data' attribute."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'data')

    def test_match_pledge_has_clr_round_num_attribute(self):
        """Test 'clr_round_num' attribute is present and is an instance of GrantCLR."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'clr_round_num')
        assert isinstance(match_pledge.clr_round_num, GrantCLR)

    def test_data_json(self):
        """Test 'data_json' property returns data attribute as valid JSON."""

        match_pledge = MatchPledgeFactory()

        assert hasattr(match_pledge, 'data_json')
        assert match_pledge.data_json == 'test string'
