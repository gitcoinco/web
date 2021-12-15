import pytest
from git.models import GitCache
from git.tests.factories.git_cache_factory import GitCacheFactory


@pytest.mark.django_db
class TestGitCache:
    """Test CLRMatch model."""

    def test_creation(self):
        """Test GitCache returned by factory is valid."""

        git_cache = GitCacheFactory()

        assert isinstance(git_cache, GitCache)

    def test_get_user(self):
        """Test get_user helper function."""

        git_cache = GitCacheFactory()
        git_cache.category = GitCache.Category.USER
        handle = git_cache.handle
        git_cache.save()

        saved = GitCache.get_user(handle)
        assert git_cache.id == saved.id

    def test_update_data(self):
        """Test update_data helper function."""

        git_cache = GitCacheFactory()
        git_cache.category = GitCache.Category.USER
        handle = git_cache.handle
        git_cache.save()

        new_data = "This is updated data".encode("utf-8")
        git_cache.update_data(new_data)

        saved = GitCache.get_user(handle)
        assert new_data == saved.data.tobytes()
