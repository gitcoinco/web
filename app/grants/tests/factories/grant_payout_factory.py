import factory
import pytest
from grants.models.grant import GrantPayout


@pytest.mark.django_db
class GrantPayoutFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantPayout

