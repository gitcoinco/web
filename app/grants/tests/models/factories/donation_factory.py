import factory
import pytest
# from dashboard.tests.factories.profile_factory import ProfileFactory
from grants.models.donation import Donation


@pytest.mark.django_db
class DonationFactory(factory.django.DjangoModelFactory):
    """Create a mock Donation for testing."""

    class Meta:
        model = Donation
