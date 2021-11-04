import factory
import pytest
from grants.models.grant_clr_calculation import GrantCLRCalculation

from .grant_clr_factory import GrantCLRFactory
from .grant_factory import GrantFactory


@pytest.mark.django_db
class GrantCLRCalculationFactory(factory.django.DjangoModelFactory):
    """Create mock GrantCLRCalculation for testing."""

    class Meta:
        model = GrantCLRCalculation

    grant = factory.SubFactory(GrantFactory)
    grantclr = factory.SubFactory(GrantCLRFactory)
