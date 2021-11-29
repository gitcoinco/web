import factory
from dashboard.tests.factories import ProfileFactory
from grants.models.subscription import Subscription

from .grant_factory import GrantFactory


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    grant = factory.SubFactory(GrantFactory)
    contributor_profile = factory.SubFactory(ProfileFactory)
