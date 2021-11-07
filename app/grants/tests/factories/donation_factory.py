import factory
import pytest
from grants.models.donation import Donation

from .contribution_factory import ContributionFactory
from dashboard.tests.factories import ProfileFactory
from .subscription_factory import SubscriptionFactory


@pytest.mark.django_db
class DonationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Donation

    profile = factory.SubFactory(ProfileFactory)
    subscription = factory.SubFactory(SubscriptionFactory)
    contribution = factory.SubFactory(ContributionFactory)
