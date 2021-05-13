# -*- coding: utf-8 -*-
"""Handle github utility related tests.

Copyright (C) 2020 Gitcoin Core

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
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.test.utils import override_settings
from django.utils import timezone

import responses
from git.utils import (
    BASE_URI, HEADERS, JSON_HEADER, TOKEN_URL, build_auth_dict, delete_issue_comment, get_auth_url, get_github_emails,
    get_github_primary_email, get_github_user_data, get_github_user_token, get_issue_comments,
    get_issue_timeline_events, get_user, is_github_token_valid, org_name, patch_issue_comment, post_issue_comment,
    post_issue_comment_reaction, repo_url, reset_token, revoke_token, search,
)
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
    def test_search(self):
        """Test the github utility search method."""
        url = 'https://api.github.com/search/users'
        responses.add(responses.GET, url, json={'total_count': '0'}, status=200)
        query = 'a-non-existent-test-string'
        params = {'q': query, 'sort': 'updated'}
        result = search(query)
        params = urlencode(params, quote_via=quote_plus)

        assert result == {'total_count': '0'}
        assert responses.calls[0].request.url == url + '?' + params
        assert responses.calls[0].response.text == '{"total_count": "0"}'

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
    def test_get_github_user_token(self):
        """Test the github utility get_github_user_token method."""
        data = {'access_token': self.user_oauth_token, 'scope': 'read:user,user:email'}
        params = {
            'code': self.callback_code,
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
        }
        params = urlencode(params, quote_via=quote_plus)
        url = settings.GITHUB_TOKEN_URL + '?' + params
        responses.add(responses.GET, settings.GITHUB_TOKEN_URL, json=data, headers=JSON_HEADER, status=200)
        responses.add(responses.GET, settings.GITHUB_TOKEN_URL, json={}, headers=JSON_HEADER, status=200)
        result = get_github_user_token(self.callback_code)
        result_no_token = get_github_user_token(self.callback_code)

        assert responses.calls[0].request.url == url
        assert responses.calls[1].request.url == url
        assert result == self.user_oauth_token
        assert result_no_token is None

    @responses.activate
    def test_get_github_user_data(self):
        """Test the github utility get_github_user_data method."""
        headers = dict({'Authorization': f'token {self.user_oauth_token}'}, **JSON_HEADER)
        data = {'login': 'gitcoin'}
        responses.add(responses.GET, 'https://api.github.com/user', json=data, headers=headers, status=200)
        result = get_github_user_data(self.user_oauth_token)

        assert result == data

    @responses.activate
    def test_get_github_user_data_failure(self):
        """Test the github utility get_github_user_data method."""
        headers = dict({'Authorization': f'token {self.user_oauth_token}'}, **JSON_HEADER)
        data = {'login': 'gitcoin'}
        responses.add(responses.GET, 'https://api.github.com/user', json=data, headers=headers, status=404)
        result = get_github_user_data(self.user_oauth_token)

        assert result == {}

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

    @responses.activate
    def test_get_github_primary_email(self):
        """Test the github utility get_github_primary_email method."""
        data = [{'primary': True, 'email': 'test@gitcoin.co'}, {'email': 'test2@gitcoin.co'}]
        url = 'https://api.github.com/user/emails'
        responses.add(responses.GET, url, json=data, headers=HEADERS, status=200)
        responses.add(responses.GET, url, json=data, headers=HEADERS, status=404)
        email = get_github_primary_email(self.user_oauth_token)
        no_email = get_github_primary_email(self.user_oauth_token)

        assert email == 'test@gitcoin.co'
        assert no_email == ''

    @responses.activate
    def test_get_github_emails(self):
        """Test the github utility get_github_emails method."""
        headers = dict({'Authorization': f'token {self.user_oauth_token}'}, **JSON_HEADER)
        data = [{'email': 'test@gitcoin.co'}, {'email': 'test2@gitcoin.co'}, {'email': 'testing@noreply.github.com'}]
        url = 'https://api.github.com/user/emails'
        responses.add(responses.GET, url, json=data, headers=headers, status=200)
        responses.add(responses.GET, url, json=data, headers=headers, status=404)
        emails = get_github_emails(self.user_oauth_token)
        no_emails = get_github_emails(self.user_oauth_token)

        assert responses.calls[0].request.url == url
        assert emails == ['test@gitcoin.co', 'test2@gitcoin.co']
        assert no_emails == []

    @responses.activate
    def test_get_issue_comments(self):
        """Test the github utility get_issue_comments method."""
        params = {'sort': 'created', 'direction': 'desc', 'per_page': 100, }
        params = urlencode(params, quote_via=quote_plus)
        owner = 'gitcoinco'
        repo = 'web'
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments?' + params
        responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
        get_issue_comments(owner, repo)

        assert responses.calls[0].request.url == url

    @responses.activate
    def test_get_issue_comments_issue(self):
        """Test the github utility get_issue_comments_issue method."""
        params = {'sort': 'created', 'direction': 'desc', 'per_page': 100, }
        params = urlencode(params, quote_via=quote_plus)
        owner = 'gitcoinco'
        repo = 'web'
        issue = 1
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}/comments'
        url = url + '?' + params
        responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
        get_issue_comments(owner, repo, issue)

        assert responses.calls[0].request.url == url

    @responses.activate
    def test_get_issue_timeline_events(self):
        """Test the github utility get_issue_timeline_events method."""
        params = {'sort': 'created', 'direction': 'desc', 'per_page': 100, 'page': 1}
        params = urlencode(params, quote_via=quote_plus)
        owner = 'gitcoinco'
        repo = 'web'
        issue = 1
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}/timeline'
        url = url + '?' + params
        responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
        get_issue_timeline_events(owner, repo, issue)

        assert responses.calls[0].request.url == url

    @responses.activate
    def test_get_user(self):
        """Test the github utility get_user method."""
        url = 'https://api.github.com/users/gitcoin?per_page=100'
        responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
        get_user('@gitcoin')

        assert responses.calls[0].request.url == url

    @responses.activate
    def test_get_user_subpath(self):
        """Test the github utility get_user method with a subpath."""
        url = 'https://api.github.com/users/gitcoin/test?per_page=100'
        responses.add(responses.GET, url, headers=HEADERS, json={}, status=200)
        get_user('@gitcoin', '/test')

        assert responses.calls[0].request.url == url

    @responses.activate
    def test_post_issue_comment(self):
        """Test the github utility post_issue_comment method."""
        owner = 'gitcoinco'
        repo = 'web'
        issue_num = 1
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/comments'
        responses.add(responses.POST, url, headers=HEADERS, json={}, status=200)
        post_issue_comment(owner, repo, issue_num, 'A comment.')

        assert responses.calls[0].request.url == url

    @responses.activate
    def test_patch_issue_comment(self):
        """Test the github utility patch_issue_comment method."""
        comment_id = 1
        owner = 'gitcoinco'
        repo = 'web'
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        responses.add(responses.PATCH, url, headers=HEADERS, json={}, status=200)
        result = patch_issue_comment(comment_id, owner, repo, 'A comment.')

        assert responses.calls[0].request.url == url
        assert result == {}

    @responses.activate
    def test_delete_issue_comment(self):
        """Test the github utility delete_issue_comment method."""
        comment_id = 1
        owner = 'gitcoinco'
        repo = 'web'
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        responses.add(responses.DELETE, url, headers=HEADERS, json={}, status=200)
        result = delete_issue_comment(comment_id, owner, repo)

        assert responses.calls[0].request.url == url
        assert result == {}

    @responses.activate
    def test_post_issue_comment_reaction(self):
        """Test the github utility post_issue_comment_reaction method."""
        comment_id = 1
        owner = 'gitcoinco'
        repo = 'web'
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions'
        responses.add(responses.POST, url, headers=HEADERS, json={}, status=200)
        post_issue_comment_reaction(owner, repo, comment_id, 'A comment.')

        assert responses.calls[0].request.url == url
