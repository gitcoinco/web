import factory
import pytest
from dashboard.tests.factories.profile_factory import ProfileFactory
from grants.models.cart_activity import CartActivity

from .grant_factory import GrantFactory


@pytest.mark.django_db
class CartActivityFactory(factory.django.DjangoModelFactory):
    """Create mock CartActivity for testing."""

    class Meta:
        model = CartActivity

    grant = factory.SubFactory(GrantFactory)
    profile = factory.SubFactory(ProfileFactory)
    action = ''