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

    