
import pytest
from grants.models.donation import Donation

from .factories.donation_factory import DonationFactory


@pytest.mark.django_db
class TestDonation:
    """Test Donation model."""

    def test_creation(self):
        donation = DonationFactory()

        assert isinstance(donation, Donation)

    def test_donation_has_a_from_address(self):
        donation = DonationFactory()

        assert hasattr(donation, 'from_address')
        assert donation.from_address == '0x0'

    def test_donation_has_a_to_address(self):
        donation = DonationFactory()

        assert hasattr(donation, 'to_address')
        assert donation.to_address == '0x0'

    def test_donation_belongs_to_profile(self):
        donation = DonationFactory()

        assert hasattr(donation, 'profile')
        assert donation.profile == None


