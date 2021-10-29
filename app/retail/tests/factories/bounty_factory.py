from datetime import datetime, timedelta

import factory
import pytest
from dashboard.models import Bounty


@pytest.mark.django_db
class BountyFactory(factory.django.DjangoModelFactory):
    """Create instance of Bounty for testing."""

    class Meta:
        model = Bounty

    web3_created = datetime.now()
    is_open = True
    expires_date = datetime.now() + timedelta(days=365)
    raw_data = ''
