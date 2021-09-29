import pytest
from grants.models.grant_category import GrantCategory

from .factories.grant_category_factory import GrantCategoryFactory


@pytest.mark.django_db
class TestGrantCategory:
    """Test GrantCategory model."""

    def test_creation(self):
        """Test GrantCategory returned by factory is valid."""

        grant_category = GrantCategoryFactory()

        assert isinstance(grant_category, GrantCategory)

    def test_grant_category_has_a_category(self):
        """Test 'category' attribute is present."""

        grant_category = GrantCategoryFactory()

        assert hasattr(grant_category, 'category')