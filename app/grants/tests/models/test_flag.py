from unittest.mock import patch

import pytest
from dashboard.models import Activity, Profile
from grants.models.flag import Flag
from grants.models.grant import Grant
from grants.tests.factories import FlagFactory
from townsquare.models import Comment


@pytest.mark.django_db
class TestFlag:
    """Test Flag model."""

    def test_creation(self):
        """Test instance of Flag returned by factory is valid."""

        flag = FlagFactory()

        assert isinstance(flag, Flag)

    def test_flag_has_associated_grant(self):
        """Test 'grant' attribute is present and is an instance of Grant."""

        flag = FlagFactory()

        assert hasattr(flag, 'grant')
        assert isinstance(flag.grant, Grant)

    def test_flag_has_associated_profile(self):
        """Test 'profile' attribute is present and is an instance of Profile."""

        flag = FlagFactory()

        assert hasattr(flag, 'profile')
        assert isinstance(flag.profile, Profile)

    def test_flag_has_comments(self):
        """Test 'comments' attribute is present."""

        flag = FlagFactory()

        assert hasattr(flag, 'comments')
        assert flag.comments == ''

    def test_flag_has_processed_attribute(self):
        """Test 'processed' attribute is present and defaults to False."""

        flag = FlagFactory()

        assert hasattr(flag, 'processed')
        assert flag.processed == False

    def test_flag_has_comments_admin(self):
        """Test 'comments_admin' attribute is present and defaults to empty string."""

        flag = FlagFactory()

        assert hasattr(flag, 'comments_admin')
        assert flag.comments_admin == ''

    def test_flag_has_tweet_attribute(self):
        """Test 'tweet' attribute is present."""

        flag = FlagFactory()

        assert hasattr(flag, 'tweet')

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
