import pytest
from faker import Faker
from git.models import GitCache
from git.tests.factories.git_cache_factory import GitCacheFactory


@pytest.mark.django_db
class TestGitCache:
    """Test CLRMatch model."""

    def test_creation(self):
        """Test GitCache returned by factory is valid."""

        git_cache = GitCacheFactory()

        assert isinstance(git_cache, GitCache)

    def test_create_user_cache(self):
        """Test create_user_cache helper function."""
        fake = Faker()

        user = fake.user_name()

        git_cache = GitCache.create_user_cache(user)
        assert git_cache.handle == user
        assert git_cache.category == GitCache.Category.USER

    def test_create_user_cache(self):
        """Test create_repo_cache helper function."""
        fake = Faker()

        user = fake.user_name()
        repo = fake.user_name()

        git_cache = GitCache.create_repo_cache(user, repo)
        assert git_cache.handle == f"{user}/{repo}"
        assert git_cache.category == GitCache.Category.REPO

    def test_create_issue_cache(self):
        """Test create_issue_cache helper function."""
        fake = Faker()

        user = fake.user_name()
        repo = fake.user_name()
        issue = fake.pyint()

        git_cache = GitCache.create_issue_cache(user, repo, issue)
        assert git_cache.handle == f"{user}/{repo}/issue/{issue}"
        assert git_cache.category == GitCache.Category.ISSUE

    def test_create_issue_comment_cache(self):
        """Test create_issue_comment_cache helper function."""
        fake = Faker()

        user = fake.user_name()
        repo = fake.user_name()
        issue = fake.pyint()
        comment = fake.pyint()

        git_cache = GitCache.create_issue_comment_cache(user, repo, issue, comment)

        assert git_cache.handle == f"{user}/{repo}/issue/{issue}/{comment}"
        assert git_cache.category == GitCache.Category.ISSUE_COMMENT

    def test_get_user(self):
        """Test get_user helper function."""
        fake = Faker()

        user = fake.user_name()
        binary_data = fake.text().encode('utf-8')

        git_cache = GitCache(handle=f"{user}", category=GitCache.Category.USER, data=binary_data)
        git_cache.save()

        saved = GitCache.get_user(user)
        assert saved.id == git_cache.id
        assert saved.category == GitCache.Category.USER
        assert bytes(saved.data) == binary_data

    def test_get_repo(self):
        """Test get_repo helper function."""
        fake = Faker()

        user = fake.user_name()
        repo = fake.user_name()
        binary_data = fake.text().encode('utf-8')

        git_cache = GitCache(handle=f"{user}/{repo}", category=GitCache.Category.REPO, data=binary_data)
        git_cache.save()

        saved = GitCache.get_repo(user, repo)
        assert saved.id == git_cache.id
        assert saved.category == GitCache.Category.REPO
        assert bytes(saved.data) == binary_data

    def test_get_issue(self):
        """Test get_issue helper function."""
        fake = Faker()

        user = fake.user_name()
        repo = fake.user_name()
        issue = fake.pyint()
        binary_data = fake.text().encode('utf-8')

        git_cache = GitCache(handle=f"{user}/{repo}/issue/{issue}", category=GitCache.Category.ISSUE, data=binary_data)
        git_cache.save()

        saved = GitCache.get_issue(user, repo, issue)
        assert saved.id == git_cache.id
        assert saved.category == GitCache.Category.ISSUE
        assert bytes(saved.data) == binary_data

    def test_get_issue_comment(self):
        """Test get_issue_comment helper function."""
        fake = Faker()

        user = fake.user_name()
        repo = fake.user_name()
        issue = fake.pyint()
        comment = fake.pyint()
        binary_data = fake.text().encode('utf-8')

        git_cache = GitCache(handle=f"{user}/{repo}/issue/{issue}/{comment}",
                             category=GitCache.Category.ISSUE_COMMENT, data=binary_data)
        git_cache.save()

        saved = GitCache.get_issue_comment(user, repo, issue, comment)
        assert saved.id == git_cache.id
        assert saved.category == GitCache.Category.ISSUE_COMMENT
        assert bytes(saved.data) == binary_data

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
