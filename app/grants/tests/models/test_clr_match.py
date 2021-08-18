import pytest
from grants.models.clr_match import CLRMatch

from .factories.clr_match_factory import CLRMatchFactory


@pytest.mark.django_db
class TestCLRMatch:
    """Test CLRMatch model."""

    def test_creation(self):
        """Test CLRMatch returned by factory is valid."""

        clr_match = CLRMatchFactory()

        assert isinstance(clr_match, CLRMatch)
