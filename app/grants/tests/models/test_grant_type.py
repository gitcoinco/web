import pytest
from grants.models.grant_type import GrantType

from .factories import GrantTypeFactory


@pytest.mark.django_db
class TestGrantType:
    def test_creation(self):
        grant_type = GrantTypeFactory()

        assert isinstance(grant_type, GrantType)
        assert grant_type.name == "TestGrantType"
