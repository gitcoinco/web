import pytest
from grants.models.grant_stat import GrantStat

from .factories.grant_stat_factory import GrantStatFactory


@pytest.mark.django_db
class TestGrantStat:
    """Test GrantStat model."""

    def test_creation(self):
        """Test GrantStat returned by factory is valid."""

        grant_stat = GrantStatFactory()

        assert isinstance(grant_stat, GrantStat)

