from unittest.mock import patch

import pytest
from dashboard.models import Activity, Profile
from grants.models.flag import Flag
from grants.models.grant import Grant
from townsquare.models import Comment

from .factories.flag_factory import FlagFactory
from .factories.profile_factory import ProfileFactory


@pytest.mark.django_db
class TestFlag:
    """Test Flag model."""

    def test_creation(self):
        """Test instance of Flag returned by factory is valid."""

        flag = FlagFactory()

        assert isinstance(flag, Flag)

    def test_flag_belongs_to_grant(self):
        """Test relation of Flag to associated Grant."""

        flag = FlagFactory()

        assert hasattr(flag, 'grant')
        assert isinstance(flag.grant, Grant)

    def test_flag_belongs_to_profile(self):
        """Test relation of Flag to associated Profile and default value."""

        flag = FlagFactory()

        assert hasattr(flag, 'profile')
        assert isinstance(flag.profile, Profile)

    def test_flag_has_comments(self):
        """Test 'comments' attribute and default value."""

        flag = FlagFactory()

        assert hasattr(flag, 'comments')
        assert flag.comments == 'Test comment'

    def test_flag_has_processed_attribute(self):
        """Test 'processed' attribute and default value."""

        flag = FlagFactory()

        assert hasattr(flag, 'processed')
        assert flag.processed == False

    def test_flag_has_comments_admin(self):
        """Test 'comments_admin' attribute and default."""

        flag = FlagFactory()

        assert hasattr(flag, 'comments_admin')
        assert flag.comments_admin == ''

    def test_flag_has_tweet_attribute(self):
        """Test 'tweet' attribute."""

        flag = FlagFactory()

        assert hasattr(flag, 'tweet')
        assert flag.tweet == ''

    def test_post_flag_method_calls_collaborators_with_appropriate_attributes(self):
        """Test post_flag() method calls filter() on Profile.objects, create() on Activity.objects, and create() on Comment.objects."""
        
        flag = FlagFactory()

        with patch.object(Profile.objects, 'filter') as filter:
            with patch.object(Activity.objects, 'create') as activity:
                with patch.object(Comment.objects, 'create') as comment:

                    flag.post_flag()

        filter.assert_called_with(handle='gitcoinbot')
        activity.assert_called_with(profile=filter().first(), activity_type='flagged_grant', grant=flag.grant)
        comment.assert_called_with(profile=filter().first(), activity=activity(), comment=f"Comment from anonymous user: {flag.comments}")
