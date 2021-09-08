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

    
