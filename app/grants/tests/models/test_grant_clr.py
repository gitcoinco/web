import pytest
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
        """Test sub_round_slug attribute is present and defailts to empty string."""

        grant_clr = GrantCLRFactory()

        assert hasattr(grant_clr, 'sub_round_slug')
        assert grant_clr.sub_round_slug == ''

    

