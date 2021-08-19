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

    def test_grant_branding_routing_policy_has_a_policy_name(self):
        """Test policy_name attribute."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'policy_name')
        assert grant_branding_routing_policy.policy_name == None

    def test_grant_branding_routing_policy_has_a_url_pattern(self):
        """Test url_pattern attribute."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'url_pattern')
        assert grant_branding_routing_policy.url_pattern == ''

    def test_grant_branding_routing_policy_has_a_banner_image(self):
        """Test banner_image attribute."""
        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()
        pass

    def test_grant_branding_routing_policy_has_a_priority_attribute(self):
        """Test priority attribute."""
        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()
        pass

    def test_grant_branding_routing_policy_has_a_background_image(self):
        """Test background_image attribute."""
        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()
        pass

    def test_grant_branding_routing_policy_has_a_inline_css_attribute(self):
        """Test inline_css attribute."""
        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()
        pass