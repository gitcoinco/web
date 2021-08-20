import pytest
from grants.models.flag import Flag

from .factories.flag_factory import FlagFactory


@pytest.mark.django_db
class TestFlag:
    """Test Flag model."""

    def test_creation(self):
        """Test instance of Flag returned by factory is valid."""

        flag = FlagFactory()

        assert isinstance(flag, Flag)
