import factory
import pytest
from git.models import GitCache


@pytest.mark.django_db
class GitCacheFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GitCache

    # Unique user handle
    handle = factory.Sequence(lambda n: f"user_handle_{n}")

    # Cycle through the choices and select one
    category = factory.Sequence(lambda n: GitCache.CATEGORY_CHOICES[n % len(GitCache.CATEGORY_CHOICES)][0])

    # Generate binary data depending on n
    data = factory.Sequence(lambda n: ("{n}" * 100).encode("utf-8"))

