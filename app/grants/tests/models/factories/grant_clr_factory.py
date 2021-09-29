from datetime import datetime, timedelta

import factory
import pytest
from grants.models.grant import GrantCLR

from .profile_factory import ProfileFactory

@pytest.mark.django_db
class GrantCLRFactory(factory.django.DjangoModelFactory):
    """Create mock GrantCLR for testing."""

    class Meta:
        model = GrantCLR

    round_num = 2
    start_date = datetime.now()
    end_date = start_date + timedelta(weeks=2)
    owner = factory.SubFactory(ProfileFactory)
