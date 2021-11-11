import pytest
from grants.models.grant import Grant, GrantCLR
from grants.models.grant_clr_calculation import GrantCLRCalculation

from .factories.grant_clr_calculation_factory import GrantCLRCalculationFactory


@pytest.mark.django_db
class TestGrantCLRCalculation:
    """Test GrantCLRCalculation model."""

    def test_creation(self):
        """Test GrantCLRCalculation returned by factory is valid."""

        grant_clr_calulation = GrantCLRCalculationFactory()

        assert isinstance(grant_clr_calulation, GrantCLRCalculation)

    def test_grant_clr_calculation_has_latest_attribute(self):
        """Test 'latest' attribute is present and defaults to False."""

        grant_clr_calulation = GrantCLRCalculationFactory()

        assert hasattr(grant_clr_calulation, 'latest')
        assert grant_clr_calulation.latest == False

    def test_grant_clr_calculation_has_active_attribute(self):
        """Test 'active' attribute is present and defaults to False."""

        grant_clr_calulation = GrantCLRCalculationFactory()

        assert hasattr(grant_clr_calulation, 'active')
        assert grant_clr_calulation.active == False

    def test_grant_clr_calculation_has_associated_grant(self):
        """Test 'grant' attribute is present and is an instance of Grant."""

        grant_clr_calculation = GrantCLRCalculationFactory()

        assert hasattr(grant_clr_calculation, 'grant')
        assert isinstance(grant_clr_calculation.grant, Grant)

    def test_grant_clr_calculation_has_associated_grant_clr(self):
        """Test 'grantclr' attribute is present and is an instance of GrantCLR."""

        grant_clr_calculation = GrantCLRCalculationFactory()

        assert hasattr(grant_clr_calculation, 'grantclr')
        assert isinstance(grant_clr_calculation.grantclr, GrantCLR)

    def test_grant_clr_calculation_has_clr_prediction_curve(self):
        """Test 'clr_prediction_curve' attribute is present and defaults to an empty list."""

        grant_clr_calculation = GrantCLRCalculationFactory()

        assert hasattr(grant_clr_calculation, 'clr_prediction_curve')
        assert grant_clr_calculation.clr_prediction_curve == []
        assert len(grant_clr_calculation.clr_prediction_curve) == 0
