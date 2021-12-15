import random

import factory
import pytest
from dashboard.tests.factories import ProfileFactory
from grants.models.cart_activity import CartActivity

from .grant_factory import GrantFactory


@pytest.mark.django_db
class CartActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartActivity

    grant = factory.SubFactory(GrantFactory)
    profile = factory.SubFactory(ProfileFactory)
    action = factory.LazyFunction(lambda: random.choice(CartActivity.ACTIONS)[0])
