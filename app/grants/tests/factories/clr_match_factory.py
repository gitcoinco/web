import factory
import pytest
from grants.models.clr_match import CLRMatch

from .contribution_factory import ContributionFactory
from .grant_factory import GrantFactory


@pytest.mark.django_db
class CLRMatchFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CLRMatch

    amount = factory.Faker('pyfloat')
    grant = factory.SubFactory(GrantFactory)
    test_payout_contribution = factory.SubFactory(ContributionFactory)
    payout_contribution = factory.SubFactory(ContributionFactory)
