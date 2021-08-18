
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

    def test_donation_has_a_token_address(self):
        donation = DonationFactory()

        assert hasattr(donation, 'token_address')
        assert donation.token_address == '0x0'

    def test_donation_has_a_token_symbol(self):
        donation = DonationFactory()

        assert hasattr(donation, 'token_symbol')
        assert donation.token_symbol == ''

    def test_donation_has_a_token_amount(self):
        donation = DonationFactory()

        assert hasattr(donation, 'token_amount')
        assert donation.token_amount == 0

    def test_donation_has_a_token_amount_usdt(self):
        donation = DonationFactory()

        assert hasattr(donation, 'token_amount_usdt')
        assert donation.token_amount_usdt == 0
    
    def test_donation_has_a_tx_id(self):
        donation = DonationFactory()

        assert hasattr(donation, 'tx_id')
        assert donation.tx_id == '0x0'

    def test_donation_has_a_network(self):
        donation = DonationFactory()

        assert hasattr(donation, 'network')
        assert donation.network == 'mainnet'

    def test_donation_has_a_donation_percentage(self):
        donation = DonationFactory()

        assert hasattr(donation, 'donation_percentage')
        assert donation.donation_percentage == 0

    def test_donation_belongs_to_subscription(self):
        donation = DonationFactory()

        assert hasattr(donation, 'subscription')
        assert donation.subscription == None

    def test_donation_belongs_to_contribution(self):
        donation = DonationFactory()

        assert hasattr(donation, 'contribution')
        assert donation.contribution == None