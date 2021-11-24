import factory
from grants.models.contribution import Contribution

from .subscription_factory import SubscriptionFactory


class ContributionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contribution

    subscription = factory.SubFactory(SubscriptionFactory)
