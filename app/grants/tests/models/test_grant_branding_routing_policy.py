import pytest
from grants.models.grant_branding_routing_policy import GrantBrandingRoutingPolicy

from .factories.grant_branding_routing_policy_factory import GrantBrandingRoutingPolicyFactory


@pytest.mark.django_db
class TestGrantBrandingRoutingPolicy:
    """Test GrantBrandingRoutingPolicy model."""

    def test_creation(self):
        """Test GrantBrandingRoutingPolicy returned by factory is valid."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert isinstance(grant_branding_routing_policy, GrantBrandingRoutingPolicy)

    