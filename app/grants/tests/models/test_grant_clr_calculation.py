import pytest
from grants.models.grant_clr_calculation import GrantCLRCalculation

from .factories.grant_clr_calculation_factory import GrantCLRCalculationFactory


@pytest.mark.django_db
class TestGrantCLRCalculation:
    """Test GrantCLRCalculation model."""

    def test_creation(self):
        """Test GrantCLRCalculation returned by factory is valid."""

        grant_clr_calulation = GrantCLRCalculationFactory()

        assert isinstance(grant_clr_calulation, GrantCLRCalculation)

    def test_clr_calculation_has_latest_attribute(self):
        """Test 'latest' attribute and default value."""

        grant_clr_calulation = GrantCLRCalculationFactory()

        assert hasattr(grant_clr_calulation, 'latest')
        assert grant_clr_calulation.latest == False


