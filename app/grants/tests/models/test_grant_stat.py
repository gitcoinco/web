import pytest
from grants.models.grant import Grant
from grants.models.grant_stat import GrantStat

from .factories.grant_stat_factory import GrantStatFactory


@pytest.mark.django_db
class TestGrantStat:
    """Test GrantStat model."""

    def test_creation(self):
        """Test GrantStat returned by factory is valid."""

        grant_stat = GrantStatFactory()

        assert isinstance(grant_stat, GrantStat)

    def test_grant_stat_belongs_to_grant(self):
        """Test association with Grant model."""

        grant_stat = GrantStatFactory()

        assert hasattr(grant_stat, 'grant')
        assert isinstance(grant_stat.grant, Grant)

    def test_grant_stat_has_data_attribute(self):
        """Test 'data' attribute."""

        grant_stat = GrantStatFactory()

        assert hasattr(grant_stat, 'data')
        assert grant_stat.data == {}
        assert len(grant_stat.data) == 0

    def test_grant_stat_has_snapshot_type(self):
        """Test 'snapshot_type' attribute."""

        grant_stat = GrantStatFactory()

        assert hasattr(grant_stat, 'snapshot_type')
        assert grant_stat.snapshot_type == ''

    
