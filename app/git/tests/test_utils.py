# -*- coding: utf-8 -*-
"""Handle github utility related tests.

Copyright (C) 2021 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test.utils import override_settings
from django.utils import timezone

import responses
from faker import Faker
from git.models import GitCache
from git.tests.factories.git_cache_factory import GitCacheFactory
from git.utils import (
    HEADERS, TOKEN_URL, _get_issue, _get_issue_comment, _get_repo, _get_user, build_auth_dict, delete_issue_comment,
    get_github_emails, get_github_primary_email, get_issue_comments, get_issue_timeline_events, github_connect,
    is_github_token_valid, org_name, patch_issue_comment, post_issue_comment, post_issue_comment_reaction, repo_url,
    reset_token, revoke_token,
)
from github import Issue, IssueComment, NamedUser, Repository
from test_plus.test import TestCase


@override_settings(BASE_URL='http://localhost:8000')
@override_settings(GITHUB_CLIENT_ID='TEST')
@override_settings(GITHUB_CLIENT_SECRET='TEST')
@override_settings(GITHUB_SCOPE='user')
class GitUtilitiesTest(TestCase):
    """Define tests for Github utils."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.callback_code = 'e7ab3584569f7b23d005'
        self.user_oauth_token = 'bcd1c26b4fb8ddcbc7685ea9be33217434ef642f'

    def test_build_auth_dict(self):
        """Test the github utility build_auth_dict method."""
        auth_dict = build_auth_dict()

        assert isinstance(auth_dict, dict)
        assert auth_dict == {
            'api_url': settings.GITHUB_API_BASE_URL,
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET
        }

    def test_repo_url(self):
        """Test the github utility repo_url method."""
        assert repo_url('https://github.com/gitcoinco/web/issues/1') == 'https://github.com/gitcoinco/web'

    def test_org_name(self):
        """Test the github utility org_name method."""
        assert org_name('https://github.com/gitcoinco/web/issues/1') == 'gitcoinco'
        assert org_name('https://github.com/gitcoinco/web/issues/1/') == 'gitcoinco'

    @responses.activate
    def test_revoke_token(self):
        """Test the github utility revoke_token method."""
        auth_dict = build_auth_dict()
        url = TOKEN_URL.format(**auth_dict)
        data = {'access_token': self.user_oauth_token}
        responses.add(responses.DELETE, url, json=data, headers=HEADERS, status=204)
        result = revoke_token(self.user_oauth_token)

        assert responses.calls[0].request.url == url
        assert result is True

    @responses.activate
    def test_reset_token(self):
        """Test the github utility reset_token method."""
        auth_dict = build_auth_dict()
        url = TOKEN_URL.format(**auth_dict)
        data = {'token': self.user_oauth_token}
        responses.add(responses.PATCH, url, json=data, headers=HEADERS, status=200)
        responses.add(responses.PATCH, url, headers=HEADERS, status=404)
        result = reset_token(self.user_oauth_token)
        result_not_found = reset_token(self.user_oauth_token)

        assert responses.calls[0].request.url == url
        assert responses.calls[1].request.url == url
        assert result == self.user_oauth_token
        assert result_not_found == ''

    @responses.activate
    def test_is_github_token_valid(self):
        """Test the github utility is_github_token_valid method."""
        now = timezone.now()
        expired = (now - timedelta(hours=2)).isoformat()
        return_false = is_github_token_valid()
        return_valid = is_github_token_valid(self.user_oauth_token, now.isoformat())
        params = build_auth_dict()
        data = {'access_token': self.user_oauth_token}
        url = TOKEN_URL.format(**params)
        responses.add(responses.POST, url, json=data, headers=HEADERS, status=200)
        return_expired = is_github_token_valid(self.user_oauth_token, expired)

        assert responses.calls[0].request.url == url
        assert return_false is False
        assert return_valid is True
        assert return_expired is True

    # @responses.activate
    # def test_get_github_primary_email(self):
    #     """Test the github utility get_github_primary_email method."""
    #     data = [{'primary': True, 'email': 'test@gitcoin.co'}, {'email': 'test2@gitcoin.co'}]
    #     url = 'https://api.github.com/user/emails'
    #     responses.add(responses.GET, url, json=data, headers=HEADERS, status=200)
    #     responses.add(responses.GET, url, json=data, headers=HEADERS, status=404)
    #     email = get_github_primary_email(self.user_oauth_token)
    #     no_email = get_github_primary_email(self.user_oauth_token)

    #     assert email == 'test@gitcoin.co'
    #     assert no_email == ''

    # @responses.activate
    # def test_get_github_emails(self):
    #     headers = dict({'Authorization': f'token {self.user_oauth_token}'})
    #     data = [{'email': 'test@gitcoin.co'}, {'email': 'test2@gitcoin.co'}, {'email': 'testing@noreply.github.com'}]
    #     url = 'https://api.github.com/user/emails'
    #     responses.add(responses.GET, url, json=data, headers=headers, status=200)
    #     responses.add(responses.GET, url, json=data, headers=headers, status=404)
    #     emails = get_github_emails(self.user_oauth_token)
    #     no_emails = get_github_emails(self.user_oauth_token)

    #     assert responses.calls[0].request.url == url
    #     assert emails == ['test@gitcoin.co', 'test2@gitcoin.co']
    #     assert no_emails == []

    # @responses.activate
    # def test_get_issue_comments(self):
    #     """Test the github utility get_issue_comments method."""
    #     params = {'sort': 'created', 'direction': 'desc', 'per_page': 100, }
    #     params = urlencode(params, quote_via=quote_plus)
    #     owner = 'gitcoinco'
    #     repo = 'web'
    #     url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments?' + params
    #     responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
    #     get_issue_comments(owner, repo)

    #     assert responses.calls[0].request.url == url

    # @responses.activate
    # def test_get_issue_comments_issue(self):
    #     """Test the github utility get_issue_comments_issue method."""
    #     params = {'sort': 'created', 'direction': 'desc', 'per_page': 100, }
    #     params = urlencode(params, quote_via=quote_plus)
    #     owner = 'gitcoinco'
    #     repo = 'web'
    #     issue = 1
    #     url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}/comments'
    #     url = url + '?' + params
    #     responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
    #     get_issue_comments(owner, repo, issue)

    #     assert responses.calls[0].request.url == url

    # @responses.activate
    # def test_get_issue_timeline_events(self):
    #     """Test the github utility get_issue_timeline_events method."""
    #     params = {'sort': 'created', 'direction': 'desc', 'per_page': 100, 'page': 1}
    #     params = urlencode(params, quote_via=quote_plus)
    #     owner = 'gitcoinco'
    #     repo = 'web'
    #     issue = 1
    #     url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}/timeline'
    #     url = url + '?' + params
    #     responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
    #     get_issue_timeline_events(owner, repo, issue)

    #     assert responses.calls[0].request.url == url

    # @responses.activate
    # def test_post_issue_comment(self):
    #     """Test the github utility post_issue_comment method."""
    #     owner = 'gitcoinco'
    #     repo = 'web'
    #     issue_num = 1
    #     url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/comments'
    #     responses.add(responses.POST, url, headers=HEADERS, json={}, status=200)
    #     post_issue_comment(owner, repo, issue_num, 'A comment.')

    #     assert responses.calls[0].request.url == url

    # @responses.activate
    # def test_patch_issue_comment(self):
    #     """Test the github utility patch_issue_comment method."""
    #     comment_id = 1
    #     owner = 'gitcoinco'
    #     repo = 'web'
    #     url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
    #     responses.add(responses.PATCH, url, headers=HEADERS, json={}, status=200)
    #     result = patch_issue_comment(comment_id, owner, repo, 'A comment.')

    #     assert responses.calls[0].request.url == url
    #     assert result == {}

    # @responses.activate
    # def test_delete_issue_comment(self):
    #     """Test the github utility delete_issue_comment method."""
    #     comment_id = 1
    #     owner = 'gitcoinco'
    #     repo = 'web'
    #     url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
    #     responses.add(responses.DELETE, url, headers=HEADERS, json={}, status=200)
    #     result = delete_issue_comment(comment_id, owner, repo)

    #     assert responses.calls[0].request.url == url
    #     assert result == {}

    # @responses.activate
    # def test_post_issue_comment_reaction(self):
    #     """Test the github utility post_issue_comment_reaction method."""
    #     comment_id = 1
    #     owner = 'gitcoinco'
    #     repo = 'web'
    #     url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions'
    #     responses.add(responses.POST, url, headers=HEADERS, json={}, status=200)
    #     post_issue_comment_reaction(owner, repo, comment_id, 'A comment.')

    #     assert responses.calls[0].request.url == url

    @responses.activate
    @patch('git.utils.github_connect')
    def test_get_user_caching(self, mock_github_connect):
        """Test the github utility _get_user method."""
        fake = Faker()

        # Create a dummy handle and some binary data that is supposed to be the serialized user
        user_handle = fake.user_name()
        user_binary_data = fake.text().encode('utf-8')

        def dump_mock(user_obj, file_obj):
            file_obj.write(user_binary_data)

        gh_user = MagicMock(spec=NamedUser)
        gh_user.update = MagicMock()

        # Mock the gh client
        gh_client = mock_github_connect()
        gh_client.load = MagicMock(return_value=gh_user)
        gh_client.dump = dump_mock
        gh_client.get_user = MagicMock(return_value=gh_user)

        ####################################################################
        # Step 1: Make the call
        ####################################################################
        returned_user = _get_user(gh_client, user_handle)
        assert returned_user == gh_user

        # Verify what was called and that the user has been cached:
        #   - expected: get_user 
        #   - not expected: loaded, update - because user is new
        gh_client.get_user.assert_called_once_with(user_handle)
        gh_client.load.assert_not_called()
        gh_user.update.assert_not_called()

        # Verify that user has been cached
        saved_user = GitCache.get_user(user_handle)

        assert saved_user.handle == user_handle
        assert saved_user.data.tobytes() == user_binary_data

        ####################################################################
        # Step 2: Repeat the call, user should be leaded from DB
        ####################################################################
        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_client.get_user.reset_mock()

        loaded_user = _get_user(gh_client, user_handle)

        # Verify what was called and that the user has been cached:
        #   - expected: load and update (for the user loaded from DB) 
        #   - not expected: get_user (because user is already in DB)
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == user_binary_data
        gh_user.update.assert_called_once()

        gh_client.get_user.assert_not_called()

        assert loaded_user == gh_user

        ####################################################################
        # Step 3: Verify correct  behavior if updating object fails
        ####################################################################

        gh_user2 = MagicMock(spec=NamedUser)
        gh_user2.update = MagicMock(side_effect=Exception())

        # Mock the gh client
        gh_client.get_user = MagicMock(return_value=gh_user2)
        gh_client.load = MagicMock(return_value=gh_user2)
        gh_client.reset_mock()

        loaded_user = _get_user(gh_client, user_handle)

        # Verify correct  behavior if loading from cached data fails
        #   - expected: load and update (for the user loaded from DB) 
        #   - also expect: get_user (because update will throw)
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == user_binary_data
        gh_user2.update.assert_called_once()
        gh_client.get_user.assert_called_once_with(user_handle)
        assert loaded_user == gh_user2

        ####################################################################
        # Step 4: Verify correct  behavior if loading from cached data fails
        ####################################################################
        gh_user3 = MagicMock(spec=NamedUser)
        gh_user3.update = MagicMock()

        # Mock the gh client
        gh_client.get_user = MagicMock(return_value=gh_user3)
        gh_client.load = MagicMock(side_effect=Exception())
        gh_client.reset_mock()

        loaded_user = _get_user(gh_client, user_handle)

        # Verify correct  behavior if loading from cached data fails
        #   - expected: load, get_user
        #   - not expected: update because load thorws 
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == user_binary_data
        gh_user3.update.assert_not_called()
        gh_client.get_user.assert_called_once_with(user_handle)

        assert loaded_user == gh_user3

    @responses.activate
    @patch('git.utils.github_connect')
    @patch('git.utils._get_user')
    def test_get_repo_caching(self, mock__get_user, mock_github_connect):
        """Test the github utility _get_repo method."""
        fake = Faker()

        # Create a dummy handle and some binary data that is supposed to be the serialized user
        user = fake.user_name()
        repo = fake.user_name()
        repo_binary_data = fake.text().encode('utf-8')

        def dump_mock(repo_obj, file_obj):
            file_obj.write(repo_binary_data)

        gh_repo = MagicMock(spec=Repository)
        gh_repo.update = MagicMock()

        gh_user = MagicMock(spec=NamedUser)
        gh_user.get_repo = MagicMock(return_value=gh_repo)

        # Mock the gh client
        gh_client = mock_github_connect()
        gh_client.load = MagicMock(return_value=gh_repo)
        gh_client.dump = dump_mock
        gh_client.get_user = MagicMock(return_value=gh_user)

        # configure the _get_user mock
        mock__get_user.return_value = gh_user

        ####################################################################
        # Step 1: Make the call
        ####################################################################
        returned_repo = _get_repo(gh_client, user, repo)
        assert returned_repo == gh_repo

        # Verify what was called and that the user has been cached:
        #   - expected: _get_user, gh_user.get_repo() 
        #   - not expected: gh_client load, update or get_user - because user is new
        mock__get_user.assert_called_with(gh_client, user)
        gh_user.get_repo.assert_called_with(repo)

        gh_client.get_user.assert_not_called()
        gh_client.load.assert_not_called()
        gh_repo.update.assert_not_called()

        # Verify that user has been cached
        saved_repo = GitCache.get_repo(user, repo)
        assert saved_repo.data.tobytes() == repo_binary_data

        ####################################################################
        # Step 2: Repeat the call, user should be leaded from DB
        ####################################################################
        mock__get_user.reset_mock()
        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_repo.reset_mock()
        gh_user.get_repo.reset_mock()

        loaded_repo = _get_repo(gh_client, user, repo)

        # Verify what was called and that the user has been cached:
        #   - expected: load and update (for the repo loaded from DB) 
        #   - not expected: _get_user, gh_client.get_user  (because user was mocked and repo is already in DB)
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == repo_binary_data
        gh_repo.update.assert_called_once()

        mock__get_user.assert_not_called()
        gh_client.get_user.assert_not_called()

        assert loaded_repo == gh_repo

        ####################################################################
        # Step 3: Verify correct  behavior if updating object fails
        ####################################################################
        gh_repo2 = MagicMock(spec=Repository)
        gh_repo2.update = MagicMock(side_effect=Exception())

        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_repo.reset_mock()
        gh_user.get_repo = MagicMock(return_value=gh_repo2)

        # Mock the gh client
        gh_client.get_user = MagicMock(return_value=gh_user)
        gh_client.load = MagicMock(return_value=gh_repo2)
        gh_client.reset_mock()

        loaded_repo = _get_repo(gh_client, user, repo)

        # Verify correct  behavior if loading from cached data fails
        #   - expected: load, update, _get_user (for the user loaded from DB) 
        #   - also expect: _get_user (because update will throw)
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == repo_binary_data
        gh_repo2.update.assert_called_once()

        mock__get_user.assert_called_with(gh_client, user)
        gh_client.get_user.assert_not_called()
        gh_user.get_repo.assert_called_once_with(repo)

        assert loaded_repo == gh_repo2

        ####################################################################
        # Step 4: Verify correct  behavior if loading from cached data fails
        ####################################################################
        gh_repo3 = MagicMock(spec=Repository)
        gh_repo3.update = MagicMock(side_effect=Exception())

        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_repo.reset_mock()
        gh_user.get_repo = MagicMock(return_value=gh_repo3)

        # Mock the gh client
        gh_client.get_user = MagicMock(return_value=gh_user)
        gh_client.load = MagicMock(side_effect=Exception())
        gh_client.reset_mock()

        loaded_repo = _get_repo(gh_client, user, repo)

        # Verify correct  behavior if loading from cached data fails
        #   - expected: load and update (for the user loaded from DB) 
        #   - also expect: get_user (because update will throw)
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == repo_binary_data
        gh_repo3.update.assert_not_called()

        mock__get_user.assert_called_with(gh_client, user)
        gh_client.get_user.assert_not_called()
        gh_user.get_repo.assert_called_once_with(repo)

        assert loaded_repo == gh_repo3


    @responses.activate
    @patch('git.utils.github_connect')
    @patch('git.utils._get_repo')
    def test_get_issue_caching(self, mock__get_repo, mock_github_connect):
        """Test the github utility _get_issue method."""
        fake = Faker()

        # Create a dummy handle and some binary data that is supposed to be the serialized user
        user = fake.user_name()
        repo = fake.user_name()
        issue = fake.pyint()
        issue_binary_data = fake.text().encode('utf-8')

        def dump_mock(repo_obj, file_obj):
            file_obj.write(issue_binary_data)

        gh_issue = MagicMock(spec=Issue)
        gh_issue.update = MagicMock()

        gh_repo = MagicMock(spec=Repository)
        gh_repo.update = MagicMock()
        gh_repo.get_issue = MagicMock(return_value=gh_issue)

        # Mock the gh client
        gh_client = mock_github_connect()
        gh_client.load = MagicMock(return_value=gh_issue)
        gh_client.dump = dump_mock

        # configure the _get_repo mock
        mock__get_repo.return_value = gh_repo

        ####################################################################
        # Step 1: Make the call
        ####################################################################
        returned_issue = _get_issue(gh_client, user, repo, issue)
        assert returned_issue == gh_issue

        # Verify what was called and that the user has been cached:
        #   - expected: _get_user, gh_repo.get_issue() 
        #   - not expected: gh_client load, update - because user is new
        mock__get_repo.assert_called_with(gh_client, user, repo)
        gh_repo.get_issue.assert_called_with(issue)

        gh_client.load.assert_not_called()
        gh_issue.update.assert_not_called()

        # Verify that user has been cached
        saved_issue = GitCache.get_issue(user, repo, issue)
        assert saved_issue.data.tobytes() == issue_binary_data

        ####################################################################
        # Step 2: Repeat the call, user should be leaded from DB
        ####################################################################
        mock__get_repo.reset_mock()
        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_repo.reset_mock()
        gh_repo.get_issue.reset_mock()

        loaded_issue = _get_issue(gh_client, user, repo, issue)

        # Verify what was called and that the user has been cached:
        #   - expected: load and update (for the repo loaded from DB) 
        #   - not expected: _get_repo, gh_repo.get_issue  (because user was mocked and repo is already in DB)
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == issue_binary_data
        gh_issue.update.assert_called_once()

        mock__get_repo.assert_not_called()
        gh_repo.get_issue.assert_not_called()

        assert loaded_issue == gh_issue


        ####################################################################
        # Step 3: Verify correct  behavior if updating object fails
        ####################################################################
        gh_issue2 = MagicMock(spec=Issue)
        gh_issue2.update = MagicMock(side_effect=Exception())

        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_repo.reset_mock()
        gh_repo.get_issue = MagicMock(return_value=gh_issue2)

        # Mock the gh client
        gh_client.get_repo = MagicMock(return_value=gh_repo)
        gh_client.load = MagicMock(return_value=gh_issue2)
        gh_client.reset_mock()

        loaded_issue = _get_issue(gh_client, user, repo, issue)

        # Verify correct  behavior if loading from cached data fails
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == issue_binary_data
        gh_issue2.update.assert_called_once()

        mock__get_repo.assert_called_with(gh_client, user, repo)
        gh_repo.get_issue.assert_called_once_with(issue)

        assert loaded_issue == gh_issue2

        ####################################################################
        # Step 4: Verify correct  behavior if loading from cached data fails
        ####################################################################
        gh_issue3 = MagicMock(spec=Issue)
        gh_issue3.update = MagicMock()

        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_repo.reset_mock()
        gh_repo.get_issue = MagicMock(return_value=gh_issue3)

        # Mock the gh client
        gh_client.get_repo = MagicMock(return_value=gh_repo)
        gh_client.load = MagicMock(side_effect=Exception())
        gh_client.reset_mock()

        loaded_issue = _get_issue(gh_client, user, repo, issue)

        # Verify correct  behavior if loading from cached data fails
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == issue_binary_data
        gh_issue3.update.assert_not_called()

        mock__get_repo.assert_called_with(gh_client, user, repo)
        gh_repo.get_issue.assert_called_once_with(issue)

        assert loaded_issue == gh_issue3

    @responses.activate
    @patch('git.utils.github_connect')
    @patch('git.utils._get_issue')
    def test_get_issue_comment_caching(self, mock__get_issue, mock_github_connect):
        """Test the github utility _get_issue_comment method."""
        fake = Faker()

        # Create a dummy handle and some binary data that is supposed to be the serialized user
        user = fake.user_name()
        repo = fake.user_name()
        issue_num = fake.pyint()
        comment_num = fake.pyint()
        comment_binary_data = fake.text().encode('utf-8')

        def dump_mock(repo_obj, file_obj):
            file_obj.write(comment_binary_data)

        gh_comment = MagicMock(spec=Repository)
        gh_comment.update = MagicMock()

        gh_issue = MagicMock(spec=Issue)
        gh_issue.update = MagicMock()
        gh_issue.get_comment = MagicMock(return_value=gh_comment)

        # Mock the gh client
        gh_client = mock_github_connect()
        gh_client.load = MagicMock(return_value=gh_comment)
        gh_client.dump = dump_mock

        # configure the _get_repo mock
        mock__get_issue.return_value = gh_issue

        ####################################################################
        # Step 1: Make the call
        ####################################################################
        returned_comment = _get_issue_comment(gh_client, user, repo, issue_num, comment_num)
        assert returned_comment == gh_comment

        # Verify what was called and that the user has been cached:
        #   - expected: _get_user, gh_issue.get_comment() 
        #   - not expected: gh_client load, update or get_user - because user is new
        mock__get_issue.assert_called_with(gh_client, user, repo, issue_num)
        gh_issue.get_comment.assert_called_with(comment_num)

        gh_client.get_user.assert_not_called()
        gh_client.load.assert_not_called()
        gh_comment.update.assert_not_called()

        # Verify that user has been cached
        saved_comment = GitCache.get_issue_comment(user, repo, issue_num, comment_num)
        assert saved_comment.data.tobytes() == comment_binary_data

        ####################################################################
        # Step 2: Repeat the call, user should be leaded from DB
        ####################################################################
        mock__get_issue.reset_mock()
        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_issue.reset_mock()
        gh_issue.get_comment.reset_mock()

        loaded_comment = _get_issue_comment(gh_client, user, repo, issue_num, comment_num)

        # Verify what was called and that the user has been cached:
        #   - expected: load and update (for the repo loaded from DB) 
        #   - not expected: _get_repo, gh_repo.get_issue  (because user was mocked and repo is already in DB)
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == comment_binary_data
        gh_comment.update.assert_called_once()

        mock__get_issue.assert_not_called()
        gh_issue.get_comment.assert_not_called()

        assert loaded_comment == gh_comment

        ####################################################################
        # Step 3: Verify correct  behavior if updating object fails
        ####################################################################
        gh_comment2 = MagicMock(spec=IssueComment)
        gh_comment2.update = MagicMock(side_effect=Exception())

        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_issue.reset_mock()
        gh_issue.get_comment = MagicMock(return_value=gh_comment2)

        # Mock the gh client
        gh_client.get_issue = MagicMock(return_value=gh_issue)
        gh_client.load = MagicMock(return_value=gh_comment2)
        gh_client.reset_mock()

        loaded_comment = _get_issue_comment(gh_client, user, repo, issue_num, comment_num)

        # Verify correct  behavior if loading from cached data fails
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == comment_binary_data
        gh_comment2.update.assert_called_once()

        mock__get_issue.assert_called_with(gh_client, user, repo, issue_num)
        gh_issue.get_comment.assert_called_with(comment_num)

        assert loaded_comment == gh_comment2

        ####################################################################
        # Step 4: Verify correct  behavior if loading from cached data fails
        ####################################################################
        gh_comment3 = MagicMock(spec=IssueComment)
        gh_comment3.update = MagicMock()

        gh_client.reset_mock()
        gh_client.load.reset_mock()
        gh_issue.reset_mock()
        gh_issue.get_comment = MagicMock(return_value=gh_comment3)

        # Mock the gh client
        gh_client.get_issue = MagicMock(return_value=gh_issue)
        gh_client.load = MagicMock(side_effect=Exception())
        gh_client.reset_mock()

        loaded_comment = _get_issue_comment(gh_client, user, repo, issue_num, comment_num)

        # Verify correct  behavior if loading from cached data fails
        gh_client.load.assert_called_once()
        assert gh_client.load.call_args[0][0].getbuffer() == comment_binary_data
        gh_comment3.update.assert_not_called()

        mock__get_issue.assert_called_with(gh_client, user, repo, issue_num)
        gh_issue.get_comment.assert_called_with(comment_num)

        assert loaded_comment == gh_comment3
