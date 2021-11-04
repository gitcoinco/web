import pytest
from grants.models.grant import Grant
from grants.models.grant_stat import GrantStat

from grants.tests.factories import GrantStatFactory


@pytest.mark.django_db
class TestGrantStat:
    """Test GrantStat model."""

    def test_creation(self):
        """Test GrantStat returned by factory is valid."""

        grant_stat = GrantStatFactory()

        assert isinstance(grant_stat, GrantStat)

    def test_grant_stat_has_associated_grant(self):
        """Test 'grant' attribute is present and is an instance of Grant."""

        grant_stat = GrantStatFactory()

        assert hasattr(grant_stat, 'grant')
        assert isinstance(grant_stat.grant, Grant)

    def test_grant_stat_has_data_attribute(self):
        """Test 'data' attribute is present and defaults to empty dictionary."""

        grant_stat = GrantStatFactory()

        assert hasattr(grant_stat, 'data')
        assert grant_stat.data == {}
        assert len(grant_stat.data) == 0

    def test_grant_stat_has_snapshot_type(self):
        """Test 'snapshot_type' attribute is present."""

        grant_stat = GrantStatFactory()

        assert hasattr(grant_stat, 'snapshot_type')
