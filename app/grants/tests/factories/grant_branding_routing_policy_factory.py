from random import randint

import factory
from grants.models.grant_branding_routing_policy import GrantBrandingRoutingPolicy


class GrantBrandingRoutingPolicyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantBrandingRoutingPolicy

    priority = factory.LazyFunction(lambda: randint(1, 255))
