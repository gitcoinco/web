import pytest
from grants.models.contribution import Contribution
from grants.models.subscription import Subscription

from .factories.contribution_factory import ContributionFactory


@pytest.mark.django_db
class TestContribution:
    """Test Contribution model."""

    def test_creation(self):
        """Test Contribution returned by factory is valid."""

        contribution = ContributionFactory()

        assert isinstance(contribution, Contribution)

    def test_contribution_has_success_attribute(self):
        """Test success attribute is present and defaults to True."""

        contribution = ContributionFactory()

        assert hasattr(contribution, 'success')
        assert contribution.success == True
        
    def test_contribution_has_tx_cleard_attribute(self):
        """Test tx_cleared attribute is present and defaults to False."""

        contribution = ContributionFactory()

        assert hasattr(contribution, 'tx_cleared')
        assert contribution.tx_cleared == False

    def test_contribution_has_tx_override_attribute(self):
        """Test tx_override attribute is present and defaults to False."""

        contribution = ContributionFactory()

        assert hasattr(contribution, 'tx_override')
        assert contribution.tx_override == False

    def test_contribution_has_tx_id_attribute(self):
        """Test tx_id attribute is present and defaults to '0x0'."""

        contribution = ContributionFactory()

        assert hasattr(contribution, 'tx_id')
        assert contribution.tx_id == '0x0'

    def test_contribution_has_split_tx_id_attribute(self):
        """Test split_tx_id is present and defaults to empty string."""

        contribution = ContributionFactory()

        assert hasattr(contribution, 'split_tx_id')
        assert contribution.split_tx_id == ''

    def test_contribution_has_split_tx_confirmed_attribute(self):
        """Test split_tx_confirmed attribute is present and defaults to False."""

        contribution = ContributionFactory()

        assert hasattr(contribution, 'split_tx_confirmed')
        assert contribution.split_tx_confirmed == False

    def test_contribution_has_associated_subscription(self):
        """Test subscription attribute is present."""

        contribution = ContributionFactory()

        assert hasattr(contribution, 'subscription')
        assert isinstance(contribution.subscription, Subscription)

    def test_contribution_has_normalized_data(self):

        pass

    def test_contribution_has_match_attribute(self):

        pass

    def test_contribution_has_originated_address(self):

        pass

    def test_contribution_has_validator_passed_attribute(self):

        pass

    def test_contribution_has_validator_comment_attribute(self):

        pass

    def test_contribution_has_profile_for_clr_attribute(self):

        pass

    def test_contribution_has_checkout_type(self):

        pass

    def test_contribution_has_anonymous_attribute(self):

        pass