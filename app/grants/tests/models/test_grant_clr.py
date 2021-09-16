import pytest
from dashboard.models import Profile
from grants.models.grant import GrantCLR

from .factories.grant_clr_factory import GrantCLRFactory


@pytest.mark.django_db
class TestGrantCLR:
    """Test GrantCLR model."""

    def test_creation(self):
        """Test GrantCLR returned by factory is valid."""

        grant_clr = GrantCLRFactory()

        assert isinstance(grant_clr, GrantCLR)

    def test_grant_clr_has_a_customer_name(self):
        """Test customer_name attribute is present and defaults to empty string."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'customer_name')
        assert grant_clr.customer_name == ''

    def test_grant_clr_has_round_num_attribute(self):
        """Test round_num attribute is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'round_num')
    
    def test_grant_clr_has_sub_round_slug_attribute(self):
        """Test sub_round_slug attribute is present and defaults to empty string."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'sub_round_slug')
        assert grant_clr.sub_round_slug == ''

    def test_grant_clr_has_display_text_attribute(self):
        """Test display_text attribute is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'display_text')

    def test_grant_clr_has_owner_attribute(self):
        """Test owner attribute is present and is an instance of Profile."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'owner')
        assert isinstance(grant_clr.owner, Profile)

    def test_grant_clr_has_is_active_attribute(self):
        """Test is_active attribute is present and defaults to False."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'is_active')
        assert grant_clr.is_active == False

    def test_grant_clr_has_start_date_attribute(self):
        """Test start_date is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'start_date')

    def test_grant_clr_has_end_date_attribute(self):
        """Test end_date is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'end_date')

    def test_grant_clr_has_grant_filters(self):
        """Test grant_filters attribute is present and defaults to an empty dictionary."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'grant_filters')
        assert grant_clr.grant_filters == {}
        assert len(grant_clr.grant_filters) == 0

    def test_grant_clr_has_subscription_filters(self):
        """Test subscription_filters attribute is present and defaults to an empty dictionary."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'subscription_filters')
        assert grant_clr.subscription_filters == {}
        assert len(grant_clr.subscription_filters) == 0

    def test_grant_clr_has_collection_filters(self):
        """Test collection_filters attribute is present and defaults to an empty dictionary."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'collection_filters')
        assert grant_clr.collection_filters == {}
        assert len(grant_clr.collection_filters) == 0

    def test_grant_clr_has_verified_threshold(self):
        """Test verified_threshold is present and defaults to 25.0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'verified_threshold')
        assert grant_clr.verified_threshold == 25.0

    def test_grant_clr_has_unverified_threshold(self):
        """Test unverified_threshold is present and defaults to 5.0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'unverified_threshold')
        assert grant_clr.unverified_threshold == 5.0

    def test_grant_clr_has_total_pot(self):
        """Test total_pot is present and defaults to 0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'total_pot')
        assert grant_clr.total_pot == 0

    def test_grant_clr_contribution_multiplier(self):
        """Test contribution_multiplier is present and defaults to 1.0."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'contribution_multiplier')
        assert grant_clr.contribution_multiplier == 1.0

    def test_grant_clr_has_logo_attribute(self):
        """Test logo attribute is present."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'logo')

    

    
