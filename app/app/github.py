'''
    Copyright (C) 2017 Gitcoin Core

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

'''
import json

from django.conf import settings

import requests

_AUTH = (settings.GITHUB_API_USER, settings.GITHUB_API_TOKEN)
BASE_URI = settings.BASE_URL.rstrip('/')
HEADERS = {'Accept': 'application/vnd.github.squirrel-girl-preview'}
V3HEADERS = {'Accept': 'application/vnd.github.v3.text-match+json'}
JSON_HEADER = {
    'Accept': 'application/json',
    'User-Agent': settings.GITHUB_APP_NAME,
    'Origin': settings.BASE_URL
}


def get_auth_url(redirect_uri='/'):
    """Build Github authorization parameters."""
    redirect_uri = BASE_URI + redirect_uri
    request_params = {
        'redirect_uri': '{}/_github/callback?redirect_uri={}'
                        .format(BASE_URI, redirect_uri),
        'client_id': settings.GITHUB_CLIENT_ID,
        'scope': settings.GITHUB_SCOPE
    }

    return settings.GITHUB_API_BASE_URL + \
        '?client_id={client_id}&scope={scope}&redirect_uri={redirect_uri}' \
        .format(**request_params)


def get_github_user_token(code, **kwargs):
    """Get the Github authorization token."""
    _params = {
        'code': code,
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET
    }
    # Add additional parameters to the request paramaters.
    _params.update(kwargs)
    response = requests.get(
        settings.GITHUB_TOKEN_URL, headers=JSON_HEADER, params=_params)
    response = response.json()
    scope = response.get('scope', None)
    if scope and scope == settings.GITHUB_SCOPE:
        access_token = response.get('access_token', None)
        return access_token
    return None


def get_github_user_data(oauth_token):
    """Get the user's github profile information.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        requests.Response: The Github user response.

    """
    headers = dict({'Authorization': 'token {}'.format(oauth_token)},
                   **JSON_HEADER)
    response = requests.get('https://api.github.com/user', headers=headers)
    if response.status_code == 200:
        return response.json()
    return response


def get_github_primary_email(oauth_token):
    """Get the primary email address associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        str: The user's primary github email address.

    """
    email = ''
    headers = dict({'Authorization': 'token {}'.format(oauth_token)},
                   **JSON_HEADER)
    response = requests.get('https://api.github.com/user/emails',
                            headers=headers)

    if response.status_code == 200:
        emails = response.json()
        for email in emails:
            if email.get('primary'):
                return email.get('email')

    return email


def get_github_emails(oauth_token):
    """Get all email addresses associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        list of str: All of the user's associated email from github.

    """
    emails = []
    headers = dict({'Authorization': 'token {}'.format(oauth_token)},
                   **JSON_HEADER)
    response = requests.get('https://api.github.com/user/emails',
                            headers=headers)

    if response.status_code == 200:
        emails = response.json()
        for email in emails:
            email_address = email.get('email')
            if email_address and 'noreply.github.com' not in email_address:
                emails.append(email_address)

    return emails


def search(query):
    """Search for a user on github.

    Args:
        q (str): The query text to match.

    Returns:
        request.Response: The github search response.

    """
    params = (
        ('q', query),
        ('sort', 'updated'),
    )

    response = requests.get(
        'https://api.github.com/search/users',
        auth=_AUTH, headers=V3HEADERS, params=params)
    return response.json()


def get_issue_comments(owner, repo, issue=None):
    """Get the comments from issues on a respository."""
    params = {
        'sort': 'created',
        'direction': 'desc',
    }
    if issue:
        url = 'https://api.github.com/repos/{}/{}/issues/{}/comments'.format(owner, repo, issue)
    else:
        url = 'https://api.github.com/repos/{}/{}/issues/comments'.format(owner, repo)
    response = requests.get(url, auth=_AUTH, headers=HEADERS, params=params)

    return response.json()


def get_user(user, sub_path=''):
    """Get the github user details."""
    url = 'https://api.github.com/users/{}{}' \
          .format(user.replace('@', ''), sub_path)
    response = requests.get(url, auth=_AUTH, headers=HEADERS)

    return response.json()


def post_issue_comment(owner, repo, issue_num, comment):
    """Post a comment on an issue."""
    url = 'https://api.github.com/repos/{}/{}/issues/{}/comments' \
          .format(owner, repo, issue_num)
    response = requests.post(url, data=json.dumps({'body': comment}),
                             auth=_AUTH)
    return response.json()


def patch_issue_comment(comment_id, owner, repo, issue_num, comment):
    """Update a comment on an issue via patch."""
    url = 'https://api.github.com/repos/{}/{}/issues/{}/comments/{}' \
          .format(owner, repo, issue_num, comment_id)
    response = requests.patch(url, data=json.dumps({'body': comment}),
                              auth=_AUTH)
    return response.json()


def delete_issue_comment(comment_id, owner, repo):
    """Remove a comment on an issue via delete."""
    url = 'https://api.github.com/repos/{}/{}/issues/comments/{}' \
          .format(owner, repo, comment_id)
    response = requests.delete(url, auth=_AUTH)
    return response.json()


def post_issue_comment_reaction(owner, repo, comment_id, content):
    """React to an issue comment."""
    url = 'https://api.github.com/repos/{}/{}/issues/comments/{}/reactions' \
          .format(owner, repo, comment_id)
    response = requests.post(
        url,
        data=json.dumps({
            'content': content
        }),
        auth=_AUTH,
        headers=HEADERS)
    return response.json()


def repo_url(issue_url):
    """Build the repository URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The repository URL.

    """
    return '/'.join(issue_url.split('/')[:-2])


def org_name(issue_url):
    """Get the organization name from an issue URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The Github organization name.

    """
    return issue_url.split('/')[3]
