import factory
import pytest
from dashboard.models import Profile
from grants.models import *


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
    
    handle = factory.Sequence(lambda n: "Contributor_%03d" % n)
    data = {}

    
@pytest.mark.django_db
class CartActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartActivity

    profile = factory.SubFactory(ProfileFactory)
    metadata = {}
    bulk = True
    latest = True
   
