import factory
import pytest
from grants.models.donation import Donation

from .contribution_factory import ContributionFactory
from .profile_factory import ProfileFactory
from .subscription_factory import SubscriptionFactory


@pytest.mark.django_db
class DonationFactory(factory.django.DjangoModelFactory):
    """Create a mock Donation for testing."""

    class Meta:
        model = Donation

    profile = factory.SubFactory(ProfileFactory)
    subscription = factory.SubFactory(SubscriptionFactory)
    contribution = factory.SubFactory(ContributionFactory)
