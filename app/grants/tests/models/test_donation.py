import pytest
from dashboard.models import Profile
from grants.models.contribution import Contribution
from grants.models.donation import Donation
from grants.models.subscription import Subscription

from .factories.donation_factory import DonationFactory


@pytest.mark.django_db
class TestDonation:
    """Test Donation model."""

    def test_creation(self):
        """Test instance of Donation returned by factory is valid."""

        donation = DonationFactory()

        assert isinstance(donation, Donation)

    def test_donation_has_a_from_address(self):
        """Test from_address attribute is present and defaults to '0x0'."""

        donation = DonationFactory()

        assert hasattr(donation, 'from_address')
        assert donation.from_address == '0x0'

    def test_donation_has_a_to_address(self):
        """Test to_address attribute is present and defaults to '0x0'."""

        donation = DonationFactory()

        assert hasattr(donation, 'to_address')
        assert donation.to_address == '0x0'

    def test_donation_belongs_to_profile(self):
        """Test profile attribute is present and is an instance of Profile."""

        donation = DonationFactory()

        assert hasattr(donation, 'profile')
        assert isinstance(donation.profile, Profile)

    def test_donation_has_a_token_address(self):
        """Test token_address attribute is present and defaults to '0x0'."""

        donation = DonationFactory()

        assert hasattr(donation, 'token_address')
        assert donation.token_address == '0x0'

    def test_donation_has_a_token_symbol(self):
        """Test token_symbol attribute is present and defaults to empty string."""

        donation = DonationFactory()

        assert hasattr(donation, 'token_symbol')
        assert donation.token_symbol == ''

    def test_donation_has_a_token_amount(self):
        """Test token_amount attribute is present and defaults to 0."""

        donation = DonationFactory()

        assert hasattr(donation, 'token_amount')
        assert donation.token_amount == 0

    def test_donation_has_a_token_amount_usdt(self):
        """Test token_amount_usdt attribute is present and defaults to 0."""

        donation = DonationFactory()

        assert hasattr(donation, 'token_amount_usdt')
        assert donation.token_amount_usdt == 0
    
    def test_donation_has_a_tx_id(self):
        """Test tx_id attribute is present and defaults to '0x0'."""

        donation = DonationFactory()

        assert hasattr(donation, 'tx_id')
        assert donation.tx_id == '0x0'

    def test_donation_has_a_network(self):
        """Test network attribute is present and defaults to 'mainnet'."""

        donation = DonationFactory()

        assert hasattr(donation, 'network')
        assert donation.network == 'mainnet'

    def test_donation_has_a_donation_percentage(self):
        """Test donation_percentage attribute is present and defaults to 0."""

        donation = DonationFactory()

        assert hasattr(donation, 'donation_percentage')
        assert donation.donation_percentage == 0

    def test_donation_has_related_subscription(self):
        """Test subscription attribute is present and is an instance of Subscription."""

        donation = DonationFactory()

        assert hasattr(donation, 'subscription')
        assert isinstance(donation.subscription, Subscription)

    def test_donation_has_related_contribution(self):
        """Test contribution attribute is present and is an instance of Contribution."""

        donation = DonationFactory()

        assert hasattr(donation, 'contribution')
        assert isinstance(donation.contribution, Contribution)
