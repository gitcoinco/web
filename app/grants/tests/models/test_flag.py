import pytest
from grants.models.flag import Flag
from grants.models.grant import Grant

from .factories.flag_factory import FlagFactory


@pytest.mark.django_db
class TestFlag:
    """Test Flag model."""

    def test_creation(self):
        """Test instance of Flag returned by factory is valid."""

        flag = FlagFactory()

        assert isinstance(flag, Flag)

    def test_flag_belongs_to_grant(self):
        """Test relation of Flag to associated Grant."""

        flag = FlagFactory()

        assert hasattr(flag, 'grant')
        assert isinstance(flag.grant, Grant)

    def test_flag_belongs_to_profile(self):
        """Test relation of Flag to associated Profile and default value."""

        flag = FlagFactory()

        assert hasattr(flag, 'profile')
        assert flag.profile == None

    def test_flag_has_comments(self):
        """Test comments attribute and default value."""

        flag = FlagFactory()

        assert hasattr(flag, 'comments')
        assert flag.comments == ''
