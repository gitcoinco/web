import pytest
from dashboard.models import Profile
from grants.models.cart_activity import CartActivity
from grants.models.grant import Grant

from grants.tests.factories import CartActivityFactory


@pytest.mark.django_db
class TestCartActivity:
    """Test CartActivity model."""

    def test_creation(self):
        """Test factory creates valid instance of CartActivity."""

        cart_activity = CartActivityFactory()

        assert isinstance(cart_activity, CartActivity)

    def test_cart_activity_has_associated_grant(self):
        """Test grant is present and is an instance of Grant."""

        cart_activity = CartActivityFactory()

        assert hasattr(cart_activity, "grant")
        assert isinstance(cart_activity.grant, Grant)

    def test_cart_activity_belongs_to_profile(self):
        """Test profile is present and is an instance of Profile."""

        cart_activity = CartActivityFactory()

        assert hasattr(cart_activity, "profile")
        assert isinstance(cart_activity.profile, Profile)

    def test_cart_activity_has_action_attribute(self):
        """Test action attribute is present."""

        cart_activity = CartActivityFactory()

        assert hasattr(cart_activity, "action")

    def test_cart_activity_has_metadata_attribute(self):
        """Test metadata attribute is present and defaults to empty dictionary."""

        cart_activity = CartActivityFactory()

        assert hasattr(cart_activity, "metadata")
        assert cart_activity.metadata == {}
        assert len(cart_activity.metadata) == 0

    def test_cart_activity_has_bulk_attribute(self):
        """Test bulk attribute is present and defaults to False."""

        cart_activity = CartActivityFactory()

        assert hasattr(cart_activity, "bulk")
        assert cart_activity.bulk == False

    def test_cart_activity_has_latest_attribute(self):
        """Test latest attribute is present and defaults to False."""

        cart_activity = CartActivityFactory()

        assert hasattr(cart_activity, "latest")
        assert cart_activity.latest == False
