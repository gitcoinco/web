
import pytest
from grants.models.donation import Donation

from .factories.donation_factory import DonationFactory


@pytest.mark.django_db
class TestDonation:
    """Test Donation model."""

    def test_creation(self):
        donation = DonationFactory()

        assert isinstance(donation, Donation)


