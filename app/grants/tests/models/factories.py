import factory
import pytest
from dashboard.models import Profile
from grants.models import *


class GrantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Grant


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
    
    handle = factory.Sequence(lambda n: "Contributor_%03d" % n)
    data = {}

    
@pytest.mark.django_db
class CartActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartActivity
    
    grant = factory.SubFactory(GrantFactory)
    profile = factory.SubFactory(ProfileFactory)
    metadata = {}
    bulk = True
    latest = True
