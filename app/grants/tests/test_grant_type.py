from unittest.mock import patch

from django.db.models import QuerySet

import pytest
from grants.models.grant import GrantCLR
from grants.models.grant_category import GrantCategory
from grants.models.grant_type import GrantType

from .factories.grant_category_factory import GrantCategoryFactory
from .factories.grant_clr_factory import GrantCLRFactory
from .factories.grant_type_factory import GrantTypeFactory


@pytest.mark.django_db
class TestGrantType:
    """Test GrantType model."""

    def test_creation(self):
        """Test instance of GrantType returned by factory is valid."""

        grant_type = GrantTypeFactory()

        assert isinstance(grant_type, GrantType)

    def test_grant_type_has_a_name(self):
        """Test 'name' attribute."""

        grant_type = GrantTypeFactory()

        assert hasattr(grant_type, 'name')
        assert grant_type.name == ''

    def test_grant_type_has_a_label(self):
        "Test 'label' attribute."

        grant_type = GrantTypeFactory()

        assert hasattr(grant_type, 'label')
        assert grant_type.label == None

    def test_grant_type_has_a_is_active_attribute(self):
        "Test 'is_active' attribute and default value."

        grant_type = GrantTypeFactory()

        assert hasattr(grant_type, 'is_active')
        assert grant_type.is_active == True

    def test_grant_type_has_a_is_visible_attribute(self):
        "Test 'is_visible' attribute and default value."

        grant_type = GrantTypeFactory()

        assert hasattr(grant_type, 'is_visible')
        assert grant_type.is_visible == True

    def test_grant_type_has_many_categories(self):
        "Test relation to GrantCategory."

        grant_categories = (GrantCategoryFactory(), GrantCategoryFactory())

        grant_type = GrantTypeFactory.create(categories=(grant_categories))

        assert hasattr(grant_type, 'categories')
        assert len(grant_type.categories.all()) == len(grant_categories)
        assert isinstance(grant_type.categories.first(), GrantCategory)

    def test_grant_type_has_a_logo(self):
        """Test 'logo' attribute."""

        grant_type = GrantTypeFactory()

        assert hasattr(grant_type, 'logo')
        assert grant_type.logo == None

    def test_clrs_method_calls_collaborator_with_appropriate_parameters(self):
        """Test GrantType.clrs method calls filter on GrantCLR.objects with appropriate parameters."""

        grant_type = GrantTypeFactory()

        with patch.object(GrantCLR.objects, 'filter') as filter:
            grant_type.clrs

        filter.assert_called_with(grant_filters__grant_type=str(grant_type.pk))

    def test_active_clrs_method_calls_collaborator_with_appropriate_parameters(self):
        """Test GrantType.active_clrs method calls filter on GrantCLR.objects with appropriate parameters."""

        grant_type = GrantTypeFactory()

        with patch.object(GrantCLR.objects, 'filter') as filter:
            grant_type.active_clrs

        filter.assert_called_with(is_active=True, grant_filters__grant_type=str(grant_type.pk))


    def test_grant_type_has_active_clrs_sum_method(self):
        """Test GrantType.active_clrs_sum method."""

        grant_type = GrantTypeFactory()

        active_clr = GrantCLRFactory()

        assert grant_type.active_clrs_sum == 0
