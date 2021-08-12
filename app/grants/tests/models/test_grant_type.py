import pytest
from grants.models.grant_type import GrantType

from .factories import GrantTypeFactory


@pytest.mark.django_db
class TestGrantType:
    def test_creation(self):
        grant_type = GrantTypeFactory()

        assert isinstance(grant_type, GrantType)

    def test_grant_type_has_a_name(self):
        grant_type = GrantTypeFactory()

        assert grant_type.name == "TestGrantType"

    def test_grant_type_has_a_label(self):
        grant_type = GrantTypeFactory()

        assert grant_type.label == "TestLabel"
