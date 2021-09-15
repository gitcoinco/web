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
