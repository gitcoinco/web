from datetime import datetime, timedelta

import factory
import pytest
from dashboard.tests.factories.profile_factory import ProfileFactory
from grants.models.grant import Grant
from grants.tests.factories.grant_type_factory import GrantTypeFactory


@pytest.mark.django_db
class GrantFactory(factory.django.DjangoModelFactory):
    """Create mock Grant for testing."""

    class Meta:
        model = Grant

    title = factory.Sequence(lambda n: f"Test grant {n}")
    grant_type = factory.SubFactory(GrantTypeFactory)
    # team_members = [factory.SubFactory(ProfileFactory)]
    github_project_url = "https://github.com/gitcoinco"
    admin_address = "0xde21F729137C5Af1b01d73aF1dC21eFfa2B8a0d6" # matching pool fund
