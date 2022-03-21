import factory
from dashboard.models import BountyFulfillment

from .bounty_factory import BountyFactory
from .profile_factory import ProfileFactory


class FulfillmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BountyFulfillment

    bounty = factory.SubFactory(BountyFactory)
    profile = factory.SubFactory(ProfileFactory)
