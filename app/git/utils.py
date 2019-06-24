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
from json import JSONDecodeError
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.utils import timezone

import dateutil.parser
import requests
from github import Github
from github.GithubException import BadCredentialsException, GithubException, UnknownObjectException
from requests.exceptions import ConnectionError
from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)

_AUTH = (settings.GITHUB_API_USER, settings.GITHUB_API_TOKEN)
BASE_URI = settings.BASE_URL.rstrip('/')
HEADERS = {'Accept': 'application/vnd.github.squirrel-girl-preview'}
V3HEADERS = {'Accept': 'application/vnd.github.v3.text-match+json'}
JSON_HEADER = {'Accept': 'application/json', 'User-Agent': settings.GITHUB_APP_NAME, 'Origin': settings.BASE_URL}
TIMELINE_HEADERS = {'Accept': 'application/vnd.github.mockingbird-preview'}
TOKEN_URL = '{api_url}/applications/{client_id}/tokens/{oauth_token}'


def github_connect(token=None):
    """Authenticate the GH wrapper with Github.

    Args:
        token (str): The Github token to authenticate with.
            Defaults to: None.

    """
    github_client = None
    if not token:
        token = settings.GITHUB_API_TOKEN

    try:
        github_client = Github(
            login_or_token=token,
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
        )
    except BadCredentialsException as e:
        logger.exception(e)
    return github_client


def get_gh_issue_details(org, repo, issue_num, token=None):
    details = {'keywords': []}
    try:
        gh_client = github_connect(token)
        org_user = gh_client.get_user(login=org)
        repo_obj = org_user.get_repo(repo)
        issue_details = repo_obj.get_issue(issue_num)
        langs = repo_obj.get_languages()
        for k, _ in langs.items():
            details['keywords'].append(k)
        details['title'] = issue_details.title
        details['description'] = issue_details.body.replace('\n', '').strip()
        details['state'] = issue_details.state
        if issue_details.state == 'closed':
            details['closed_at'] = issue_details.closed_at.isoformat()
            details['closed_by'] = issue_details.closed_by.name
    except UnknownObjectException:
        return {}
    return details


def get_gh_issue_state(org, repo, issue_num):
    gh_client = github_connect()
    org_user = gh_client.get_user(login=org)
    repo_obj = org_user.get_repo(repo)
    issue_details = repo_obj.get_issue(issue_num)
    return issue_details.state


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


def check_github(profile):
    """Check whether or not the provided username is present in the payload as active user.

    Args:
        profile (str): The profile username to be validated.

    Returns:
        dict: A dictionary containing status and user data.

    """
    user = search_github(profile + ' in:login type:user')
    response = {'status': 200, 'user': False}
    user_items = user.get('items', [])

    if user_items and user_items[0].get('login', '').lower() == profile.lower():
        response['user'] = user_items[0]
    return response


def search_github(q):
    params = (('q', q), ('sort', 'updated'), )
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
    github_callback = reverse('social:begin', args=('github', ))
    redirect_params = {'next': BASE_URI + redirect_uri}
    redirect_uri = urlencode(redirect_params, quote_via=quote_plus)

    params = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'scope': settings.GITHUB_SCOPE,
        'next': f'{BASE_URI}{github_callback}?{redirect_uri}'
    }
    auth_url = urlencode(params, quote_via=quote_plus)

    return settings.GITHUB_AUTH_BASE_URL + f'?{auth_url}'


def get_github_user_token(code, **kwargs):
    """Get the Github authorization token."""
    _params = {'code': code, 'client_id': settings.GITHUB_CLIENT_ID, 'client_secret': settings.GITHUB_CLIENT_SECRET}
    # Add additional parameters to the request paramaters.
    _params.update(kwargs)
    response = requests.get(settings.GITHUB_TOKEN_URL, headers=JSON_HEADER, params=_params)
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


def get_github_event_emails(oauth_token, username):
    """Get all email addresses associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        list of str: All of the user's associated email from github.

    """
    emails = []
    headers = JSON_HEADER
    if oauth_token:
        headers = dict({'Authorization': f'token {oauth_token}'}, **JSON_HEADER)
    response = requests.get(f'https://api.github.com/users/{username}/events/public', headers=headers)

    userinfo = get_user(username)
    user_name = userinfo.get('name', '')
    print(user_name)

    if response.status_code == 200:
        events = response.json()
        for event in events:
            payload = event.get('payload', {})
            for commit in payload.get('commits', []):
                author = commit.get('author', {})
                email = author.get('email', {})
                name = author.get('name', {})
                if name and username and user_name:
                    append_email = name.lower() == username.lower() or name.lower() == user_name.lower() \
                        and email and 'noreply.github.com' not in email
                    if append_email:
                        emails.append(email)

    return set(emails)


def get_github_emails(oauth_token):
    """Get all email addresses associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        list of str: All of the user's associated email from git.

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


def get_emails_by_category(username):
    from dashboard.models import Profile
    to_emails = {}
    to_profiles = Profile.objects.filter(handle__iexact=username)
    if to_profiles.exists():
        to_profile = to_profiles.first()
        if to_profile.github_access_token:
            to_emails['primary'] = get_github_emails(to_profile.github_access_token)
        if to_profile.email:
            to_emails['github_profile'] = to_profile.email
    to_emails['events'] = []
    for email in get_github_event_emails(None, username):
        to_emails['events'].append(email)
    return to_emails


def get_emails_master(username):
    emails_by_category = get_emails_by_category(username)
    emails = []
    for category, to_email in emails_by_category.items():
        if type(to_email) is str:
            emails.append(to_email)
        if type(to_email) is list:
            for email in to_email:
                emails.append(email)
    return list(set(emails))


def search(query):
    """Search for a user on github.

    Args:
        query (str): The query text to match.

    Returns:
        request.Response: The github search response.

    """
    params = (('q', query), ('sort', 'updated'), )

    try:
        response = requests.get('https://api.github.com/search/users', auth=_AUTH, headers=V3HEADERS, params=params)
        return response.json()
    except Exception as e:
        logger.error("could not search GH - Reason: %s - query: %s", e, query)
    return {}


def search_user(query, token=None):
    """Search for a user on github.

    Args:
        query (str): The query text to match.
        token (str): The user's Github token to be used to perform the search.

    Returns:
        dict: The first matching github user dictionary.

    """
    paginated_list = search_users(query, token)
    try:
        user_obj = paginated_list[0]
        return {
            'avatar_url': user_obj.avatar_url,
            'login': user_obj.login,
            'text': user_obj.login,
            'email': user_obj.email,
        }
    except IndexError:
        pass
    except Exception as e:
        logger.error(e)
    return {}


def search_users(query, token=None):
    """Search for a user on github.

    Args:
        query (str): The query text to match.
        token (str): The user's Github token to be used to perform the search.

    Returns:
        github.PaginatedList: The pygithub paginator object of all results if many True.

    """
    gh_client = github_connect(token)
    try:
        paginated_list = gh_client.search_users(query)
        return paginated_list
    except Exception as e:
        logger.error(e)
        return []


def get_issue_comments(owner, repo, issue=None, comment_id=None):
    """Get the comments from issues on a respository.
    PLEASE NOTE CURRENT LIMITATION OF 100 COMMENTS.

    Args:
        owner (str): Owner of the repo
        repo (str): Name of the repo
        issue (int): Issue number (optional)

    Returns:
        requests.Response: The GitHub comments response.
    """
    params = {
        'sort': 'created',
        'direction': 'desc',
        'per_page': 100,  # TODO traverse/concat pages: https://developer.github.com/v3/guides/traversing-with-pagination/
    }
    if issue:
        if comment_id:
            url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        else:
            url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}/comments'
    else:
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments'

    try:
        response = requests.get(url, auth=_AUTH, headers=HEADERS, params=params)
        return response.json()
    except Exception as e:
        logger.error(
            "could not get issue comments - Reason: %s - owner: %s repo: %s issue: %s comment_id: %s status code: %s",
            e, owner, repo, issue, comment_id, response.status_code
        )
    return {}


def get_issues(owner, repo, page=1, state='open'):
    """Get the open issues on a respository."""
    params = {'state': state, 'sort': 'created', 'direction': 'desc', 'page': page, 'per_page': 100, }
    url = f'https://api.github.com/repos/{owner}/{repo}/issues'

    try:
        response = requests.get(url, auth=_AUTH, headers=HEADERS, params=params)
        return response.json()
    except Exception as e:
        logger.error(
            "could not get issues - Reason: %s - owner: %s repo: %s page: %s state: %s status code: %s",
            e, owner, repo, page, state, response.status_code
        )
    return {}


def get_issue_timeline_events(owner, repo, issue, page=1):
    """Get the timeline events for a given issue.

    PLEASE NOTE CURRENT LIMITATION OF 100 EVENTS.
    PLEASE NOTE GITHUB API FOR THIS IS SUBJECT TO CHANGE.
    (See https://developer.github.com/changes/2016-05-23-timeline-preview-api/ for more info.)

    Args:
        owner (str): Owner of the repo
        repo (str): Name of the repo
        issue (int): Issue number

    Returns:
        requests.Response: The GitHub timeline response.
    """
    params = {'sort': 'created', 'direction': 'desc', 'per_page': 100, 'page': page, }
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue}/timeline'
    try:
        # Set special header to access timeline preview api
        response = requests.get(url, auth=_AUTH, headers=TIMELINE_HEADERS, params=params)
        return response.json()
    except Exception as e:
        logger.error(
            "could not get timeline events - Reason: %s - %s %s %s %s", e, owner, repo, issue, response.status_code
        )
    return {}


def get_interested_actions(github_url, username, email=''):
    activity_event_types = ['commented', 'cross-referenced', 'merged', 'referenced', 'review_requested', ]

    owner = org_name(github_url)
    repo = repo_name(github_url)
    issue_num = issue_number(github_url)
    should_continue_loop = True
    all_actions = []
    page = 1
    while should_continue_loop:
        actions = get_issue_timeline_events(owner, repo, issue_num, page)
        should_continue_loop = len(actions) == 100
        all_actions = all_actions + actions
        page += 1
    actions_by_interested_party = []

    for action in all_actions:
        gh_user = None
        gh_email = None
        # GitHub might populate actor OR user OR neither for some events
        if 'actor' in action:
            gh_user = action['actor']['login']
        elif 'user' in action:
            gh_user = action['user']['login']

        if action['event'] == 'cross-referenced':
            pr_num = action.get('source', {}).get('issue', {}).get('number', '')
            pr_repo_owner, pr_repo = action.get('source', {}).get('issue', {}) \
                .get('repository', {}).get('full_name', '/').split('/')

            should_continue_loop = True
            all_pr_actions = []
            page = 1
            while should_continue_loop:
                pr_actions = get_issue_timeline_events(pr_repo_owner, pr_repo, pr_num, page)
                should_continue_loop = len(pr_actions) == 100
                all_pr_actions = all_pr_actions + pr_actions
                page += 1

            for pr_action in all_pr_actions:
                pr_action['pr_url'] = pr_repo_owner + '/' + pr_repo + '/' + str(pr_num) + '/' + str(page)
                if 'actor' in pr_action:
                    if (pr_action['actor']):
                        gh_user = pr_action['actor']['login']
                    if gh_user.lower() == username.lower() and pr_action['event'] in activity_event_types:
                        actions_by_interested_party.append(pr_action)
                    elif username == '*':
                        actions_by_interested_party.append(pr_action)
                elif 'committer' in pr_action:
                    gh_email = pr_action['committer']['email']
                    if gh_email and gh_email == email:
                        actions_by_interested_party.append(pr_action)

        if gh_user and gh_user.lower() == username.lower() and action['event'] in activity_event_types:
            actions_by_interested_party.append(action)
    return actions_by_interested_party


def get_user(user, sub_path=''):
    """Get the github user details."""
    user = user.replace('@', '')
    url = f'https://api.github.com/users/{user}{sub_path}'
    response = requests.get(url, auth=_AUTH, headers=HEADERS)

    try:
        response_dict = response.json()
    except JSONDecodeError:
        response_dict = {}
    return response_dict


def get_notifications():
    """Get the github notifications."""
    url = f'https://api.github.com/notifications?all=1'
    try:
        response = requests.get(url, auth=_AUTH, headers=HEADERS)
        return response.json()
    except Exception as e:
        logger.error("could not get notifications - Reason: %s", e)
    return {}


def get_gh_notifications(login=None):
    """Get the Github notifications for Gitcoin Bot."""
    gh_client = github_connect()
    if login:
        repo_user = gh_client.get_user(login=login)
    else:
        repo_user = gh_client.get_user()
    notifications = repo_user.get_notifications(all=True)
    return notifications


def post_issue_comment(owner, repo, issue_num, comment):
    """Post a comment on an issue."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_num}/comments'
    try:
        response = requests.post(url, data=json.dumps({'body': comment}), auth=_AUTH)
        return response.json()
    except Exception as e:
        logger.error(
            "could not post issue comment - Reason: %s - %s %s %s %s", e, comment, owner, repo, response.status_code
        )
    return {}


def patch_issue_comment(comment_id, owner, repo, comment):
    """Update a comment on an issue via patch."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
    try:
        response = requests.patch(url, data=json.dumps({'body': comment}), auth=_AUTH)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(
            "could not patch issue comment - Reason: %s - %s %s %s %s", e, comment_id, owner, repo, response.status_code
        )
    return {}


def delete_issue_comment(comment_id, owner, repo):
    """Remove a comment on an issue via delete."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
    try:
        response = requests.delete(url, auth=_AUTH)
        return response.json()
    except ValueError:
        logger.error(
            "could not delete issue comment because JSON response could not be decoded: %s %s %s %s %s",
            comment_id, owner, repo, response.status_code, response.text
        )
    except Exception as e:
        logger.error(
            "could not delete issue comment - Reason: %s: %s %s %s %s %s",
            e, comment_id, owner, repo, response.status_code, response.text
        )
    return {}


def post_issue_comment_reaction(owner, repo, comment_id, content):
    """React to an issue comment."""
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions'
    try:
        response = requests.post(url, data=json.dumps({'content': content}), auth=_AUTH, headers=HEADERS)
        return response.json()
    except Exception as e:
        logger.error(
            "could not post issue reaction - Reason: %s - %s %s %s %s",
            e, comment_id, owner, repo, response.status_code
        )
    return {}


def get_url_dict(issue_url):
    """Get the URL dictionary with specific data we care about.

    Args:
        issue_url (str): The Github issue URL.

    Raises:
        IndexError: The exception is raised if accessing a necessary index fails.

    Returns:
        dict: A mapping of details for the specified issue URL.

    """
    try:
        return {
            'org': issue_url.split('/')[3],
            'repo': issue_url.split('/')[4],
            'issue_num': int(issue_url.split('/')[6]),
        }
    except IndexError as e:
        logger.warning(e)
        return {'org': org_name(issue_url), 'repo': repo_name(issue_url), 'issue_num': int(issue_number(issue_url))}


def repo_url(issue_url):
    """Build the repository URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The repository URL.

    """
    try:
        return '/'.join(issue_url.split('/')[:-2])
    except IndexError:
        return ''


def org_name(issue_url):
    """Get the organization name from an issue URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The Github organization name.

    """
    try:
        return issue_url.split('/')[3]
    except IndexError:
        return ''


def repo_name(issue_url):
    """Get the repo name from an issue URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The Github repo name.

    """
    try:
        return issue_url.split('/')[4]
    except IndexError:
        return ''


def issue_number(issue_url):
    """Get the issue_number from an issue URL.

    Args:
        issue_url (str): The Github issue URL.

    Returns:
        str: The Github issue_number

    """
    try:
        return issue_url.split('/')[6]
    except IndexError:
        return ''


def get_current_ratelimit(token=None):
    """Get the current Github API ratelimit for the provided token."""
    gh_client = github_connect(token)
    try:
        return gh_client.get_rate_limit()
    except GithubException:
        return {}
