import factory
import pytest
from grants.models.clr_match import CLRMatch

from .grant_factory import GrantFactory


@pytest.mark.django_db
class CLRMatchFactory(factory.django.DjangoModelFactory):
    """Create a mock CLRMatch for testing."""

    class Meta:
        model = CLRMatch 

    amount = 0.0
    grant = factory.SubFactory(GrantFactory)
