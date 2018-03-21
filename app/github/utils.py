# -*- coding: utf-8 -*-
"""Handle miscellaneous logic and utilities.

Copyright (C) 2018 Gitcoin Core

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
import json
import logging
from datetime import timedelta
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.utils import timezone

import dateutil.parser
import requests
import rollbar
from requests.exceptions import ConnectionError
from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)

_AUTH = (settings.GITHUB_API_USER, settings.GITHUB_API_TOKEN)
BASE_URI = settings.BASE_URL.rstrip('/')
HEADERS = {'Accept': 'application/vnd.github.squirrel-girl-preview'}
V3HEADERS = {'Accept': 'application/vnd.github.v3.text-match+json'}
JSON_HEADER = {
    'Accept': 'application/json',
    'User-Agent': settings.GITHUB_APP_NAME,
    'Origin': settings.BASE_URL
}
TOKEN_URL = '{api_url}/applications/{client_id}/tokens/{oauth_token}'


def build_auth_dict(oauth_token):
    """Collect authentication details.

    Args:
        oauth_token (str): The Github OAuth token.

    Returns:
        dict: An authentication dictionary.

    """
    return {
        'api_url': settings.GITHUB_API_BASE_URL,
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'oauth_token': oauth_token
    }


def search_github(q):

    params = (
        ('q', q),
        ('sort', 'updated'),
    )
    response = requests.get('https://api.github.com/search/users', headers=HEADERS, params=params)
    return response.json()


def is_github_token_valid(oauth_token=None, last_validated=None):
    """Check whether or not a Github OAuth token is valid.

    Args:
        access_token (str): The Github OAuth token.

    Returns:
        bool: Whether or not the provided OAuth token is valid.

    """
    # If no OAuth token was provided, no checks necessary.
    if not oauth_token:
        return False

    # If validation datetime string is passed, parse it to datetime.
    if last_validated:
        try:
            last_validated = dateutil.parser.parse(last_validated)
        except ValueError:
            print('Validation of date failed.')
            last_validated = None

    # Check whether or not the user's access token has been validated recently.
    if oauth_token and last_validated:
        if (timezone.now() - last_validated) < timedelta(hours=1):
            return True

    _params = build_auth_dict(oauth_token)
    _auth = (_params['client_id'], _params['client_secret'])
    url = TOKEN_URL.format(**_params)
    try:
        response = requests.get(url, auth=_auth, headers=HEADERS)
    except ConnectionError as e:
        if not settings.ENV == 'local':
            logger.error(e)
        else:
            print(e, '- No connection available. Unable to authenticate with Github.')
        return False

    if response.status_code == 200:
        return True
    return False


def revoke_token(oauth_token):
    """Revoke the specified token."""
    _params = build_auth_dict(oauth_token)
    _auth = (_params['client_id'], _params['client_secret'])
    url = TOKEN_URL.format(**_params)
    response = requests.delete(url, auth=_auth, headers=HEADERS)
    if response.status_code == 204:
        return True
    return False


def reset_token(oauth_token):
    """Reset the provided token.

    Args:
        access_token (str): The Github OAuth token.

    Returns:
        str: The new Github OAuth token.

    """
    _params = build_auth_dict(oauth_token)
    _auth = (_params['client_id'], _params['client_secret'])
    url = TOKEN_URL.format(**_params)
    response = requests.post(url, auth=_auth, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get('token')
    return ''


def get_auth_url(redirect_uri='/'):
    """Build the Github authorization URL.

    Args:
        redirect_uri (str): The redirect URI to be used during authentication.

    Attributes:
        github_callback (str): The local path to the Github callback view.
        redirect_params (dict): The redirect paramaters to URL encode.
        params (dict): The URL parameters to encode.
        auth_url (str): The URL encoded Github authentication parameters.

    Returns:
        str: The Github authentication URL.

    """
    github_callback = reverse('github:github_callback')
    redirect_params = {'redirect_uri': BASE_URI + redirect_uri}
    redirect_uri = urlencode(redirect_params, quote_via=quote_plus)

    params = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'scope': settings.GITHUB_SCOPE,
        'redirect_uri': f'{BASE_URI}{github_callback}?{redirect_uri}'
    }
    auth_url = urlencode(params, quote_via=quote_plus)

    return settings.GITHUB_AUTH_BASE_URL + f'?{auth_url}'


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
    if scope:
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
    headers = dict({'Authorization': f'token {oauth_token}'}, **JSON_HEADER)
    response = requests.get('https://api.github.com/user', headers=headers)
    if response.status_code == 200:
        return response.json()
    return {}


def get_github_primary_email(oauth_token):
    """Get the primary email address associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        str: The user's primary github email address.

    """
    headers = dict({'Authorization': f'token {oauth_token}'}, **JSON_HEADER)
    response = requests.get('https://api.github.com/user/emails', headers=headers)

    if response.status_code == 200:
        emails = response.json()
        for email in emails:
            if email.get('primary'):
                return email.get('email', '')

    return ''


def get_github_emails(oauth_token):
    """Get all email addresses associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        list of str: All of the user's associated email from github.

    """
    emails = []
    headers = dict({'Authorization': f'token {oauth_token}'}, **JSON_HEADER)
    response = requests.get('https://api.github.com/user/emails', headers=headers)

    if response.status_code == 200:
        email_data = response.json()
        for email in email_data:
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

    response = requests.get('https://api.github.com/search/users',
                            auth=_AUTH, headers=V3HEADERS, params=params)
    return response.json()


def get_issue_comments(owner, repo, issue=None, comment_id=None):
    """Get the comments from issues on a respository."""
    params = {
        'sort': 'created',
        'direction': 'desc',
    }
    if issue:
        if comment_id:
            url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        else:
            url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}/comments'
    else:
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments'

    response = requests.get(url, auth=_AUTH, headers=HEADERS, params=params)

    return response.json()


def get_user(user, sub_path=''):
    """Get the github user details."""
    user = user.replace('@', '')
    url = f'https://api.github.com/users/{user}{sub_path}'
    response = requests.get(url, auth=_AUTH, headers=HEADERS)

    return response.json()


def get_notifications():
    """Get the github notifications."""
    url = f'https://api.github.com/notifications?all=1'
    response = requests.get(url, auth=_AUTH, headers=HEADERS)

    return response.json()


def post_issue_comment(owner, repo, issue_num, comment):
    """Post a comment on an issue."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/comments'
    response = requests.post(url, data=json.dumps({'body': comment}), auth=_AUTH)
    return response.json()


def patch_issue_comment(comment_id, owner, repo, comment):
    """Update a comment on an issue via patch."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
    response = requests.patch(url, data=json.dumps({'body': comment}), auth=_AUTH)
    if response.status_code == 200:
        return response.json()
    rollbar.report_message(
        'Github issue comment patch returned non-200 status code', 'warning',
        request=response.request,
        extra_data={'status_code': response.status_code, 'reason': response.reason})
    return {}


def delete_issue_comment(comment_id, owner, repo):
    """Remove a comment on an issue via delete."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
    try:
        response = requests.delete(url, auth=_AUTH)
        return response.json()
    except ValueError:
        logger.error(f"could not delete issue comment because JSON response could not be decoded: {comment_id}, {owner}, {repo}.  {response.status_code}, {response.text} ")
    except Exception:
        return {}


def post_issue_comment_reaction(owner, repo, comment_id, content):
    """React to an issue comment."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions'
    response = requests.post(
        url, data=json.dumps({'content': content}), auth=_AUTH, headers=HEADERS)
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


def repo_name(issue_url):
    """Get the repo name from an issue URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The Github repo name.

    """
    return issue_url.split('/')[4]


def issue_number(issue_url):
    """Get the issue_number from an issue URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The Github issue_number

    """
    return issue_url.split('/')[6]
