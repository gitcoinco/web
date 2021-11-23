from django.db.models.fields.files import ImageFieldFile

import pytest
from grants.models.grant_branding_routing_policy import GrantBrandingRoutingPolicy

from grants.tests.factories import GrantBrandingRoutingPolicyFactory


@pytest.mark.django_db
class TestGrantBrandingRoutingPolicy:
    """Test GrantBrandingRoutingPolicy model."""

    def test_creation(self):
        """Test GrantBrandingRoutingPolicy returned by factory is valid."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert isinstance(grant_branding_routing_policy, GrantBrandingRoutingPolicy)

    def test_grant_branding_routing_policy_has_a_policy_name(self):
        """Test policy_name attribute is present."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'policy_name')

    def test_grant_branding_routing_policy_has_a_url_pattern(self):
        """Test url_pattern attribute is present."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'url_pattern')

    def test_grant_branding_routing_policy_has_a_banner_image(self):
        """Test banner_image attribute is present."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'banner_image')
        assert isinstance(grant_branding_routing_policy.banner_image, ImageFieldFile)

    def test_grant_branding_routing_policy_has_a_priority_attribute(self):
        """Test priority attribute is present."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'priority')

    def test_grant_branding_routing_policy_has_a_background_image(self):
        """Test background_image attribute is present."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'background_image')

    def test_grant_branding_routing_policy_has_a_inline_css_attribute(self):
        """Test inline_css attribute is present and defaults to empty string."""

        grant_branding_routing_policy = GrantBrandingRoutingPolicyFactory()

        assert hasattr(grant_branding_routing_policy, 'inline_css')
        assert grant_branding_routing_policy.inline_css == ''
