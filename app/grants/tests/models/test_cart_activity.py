import pytest
from dashboard.models import Profile
from grants.models.cart_activity import CartActivity
from grants.models.grant import Grant

from .factories.cart_activity_factory import CartActivityFactory


@pytest.mark.django_db
class TestCartActivity:
    """Test CartActivity model."""

    def test_creation(self):
        """Test factory creates valid instance of CartActivity."""

        cart_activity = CartActivityFactory()

        assert isinstance(cart_activity, CartActivity)

