import pytest
from grants.models.contribution import Contribution

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
        
        pass

    def test_contribution_has_tx_override_attribute(self):

        pass

    def test_contribution_has_tx_id_attribute(self):

        pass

    def test_contribution_has_split_tx_id_attribute(self):

        pass

    def test_contribution_has_split_tx_confirmed_attribute(self):

        pass

    def test_contribution_has_associated_subscription(self):

        pass

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