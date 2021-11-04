import factory
from grants.models.grant_branding_routing_policy import GrantBrandingRoutingPolicy


class GrantBrandingRoutingPolicyFactory(factory.django.DjangoModelFactory):
    """Create mock GrantBrandingRoutingPolicy for testing."""

    class Meta:
        model = GrantBrandingRoutingPolicy

    priority = 1
