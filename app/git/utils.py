# -*- coding: utf-8 -*-
"""Handle miscellaneous logic and utilities.

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
import json
import logging
from datetime import timedelta
from io import BytesIO
from urllib.parse import quote_plus, urlencode

from django.conf import settings
from django.utils import timezone

import dateutil.parser
import requests
from github import Github
from github.GithubException import BadCredentialsException, GithubException, UnknownObjectException
from requests.exceptions import ConnectionError
from rest_framework.reverse import reverse

from .models import GitCache

logger = logging.getLogger(__name__)

BASE_URI = settings.BASE_URL.rstrip('/')
HEADERS = {'Accept': 'application/vnd.github.v3+json'}
TOKEN_URL = '{api_url}/applications/{client_id}/token'


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
        github_client = Github(login_or_token=token)
    except BadCredentialsException as e:
        logger.exception(e)
    return github_client


def _get_repo(gh_client, user, repo_name):
    """Internal function to retrieve repositories
    
    This function will attempt to retrieve the repository from cache and update it. 
    If that fails, the repo will be retreived via API 
    """
    ret = None
    cached_obj = None

    # We'll attempt to load the repo data from the cache, deserialize the data and update it
    try:
        cached_obj = GitCache.get_repo(user, repo_name)
        _temp_object = gh_client.load(BytesIO(cached_obj.data))
        _temp_object.update()
        # Only set ret on the happy path. If anything fails, it is preffered to read the object from GH again.
        ret = _temp_object
    except GitCache.DoesNotExist:
        logger.debug("Repo not found in cache")
    except Exception:
        logger.error("Failed to load repo from cache", exc_info=True)

    if not ret:
        org_user = _get_user(gh_client, user)
        ret = org_user.get_repo(repo_name)

    # Cache the data
    if ret:
        if not cached_obj:
            cached_obj = GitCache.create_repo_cache(user, repo_name)

        data_dump = BytesIO()
        gh_client.dump(ret, data_dump)
        cached_obj.update_data(data_dump.getbuffer())

    return ret


def _get_issue(gh_client, user, repo_name, issue_num):
    """Internal function to retrieve issues
    
    This function will attempt to retrieve the issue from cache and update it. 
    If that fails, the repo will be retreived via API 
    """
    ret = None
    cached_obj = None

    # We'll attempt to load the issue data from the cache, deserialize the data and update it
    try:
        cached_obj = GitCache.get_issue(user, repo_name, issue_num)
        _temp_object = gh_client.load(BytesIO(cached_obj.data))
        _temp_object.update()
        # Only set ret on the happy path. If anything fails, it is preffered to read the object from GH again.
        ret = _temp_object
    except GitCache.DoesNotExist:
        logger.debug("Issue not found in cache")
    except Exception:
        logger.error("Failed to load issue from cache", exc_info=True)

    if not ret:
        repo = _get_repo(gh_client, user, repo_name)
        ret = repo.get_issue(issue_num)

    # Cache the data
    if ret:
        if not cached_obj:
            cached_obj = GitCache.create_issue_cache(user, repo_name, issue_num)

        data_dump = BytesIO()
        gh_client.dump(ret, data_dump)
        cached_obj.update_data(data_dump.getbuffer())

    return ret


def _get_issue_comment(gh_client, user, repo_name, issue_num, comment_num):
    """Internal function to retrieve comments
    
    This function will attempt to retrieve the comment from cache and update it. 
    If that fails, the repo will be retreived via API 
    """
    ret = None
    cached_obj = None

    # We'll attempt to load the comment data from the cache, deserialize the data and update it
    try:
        cached_obj = GitCache.get_issue_comment(user, repo_name, issue_num, comment_num)
        _temp_object = gh_client.load(BytesIO(cached_obj.data))
        _temp_object.update()
        # Only set ret on the happy path. If anything fails, it is preffered to read the object from GH again.
        ret = _temp_object
    except GitCache.DoesNotExist:
        logger.debug("Comment not found in cache")
    except Exception:
        logger.error("Failed to load comment from cache", exc_info=True)

    if not ret:
        issue = _get_issue(gh_client, user, repo_name, issue_num)
        ret = issue.get_comment(comment_num)

    # Cache the data
    if ret:
        if not cached_obj:
            cached_obj = GitCache.create_issue_comment_cache(user, repo_name, issue_num, comment_num)

        data_dump = BytesIO()
        gh_client.dump(ret, data_dump)
        cached_obj.update_data(data_dump.getbuffer())

    return ret


def get_issue_details(org, repo, issue_num, token=None):
    details = {'keywords': []}
    try:
        gh_client = github_connect(token)
        repo_obj = _get_repo(gh_client, org, repo)
        issue_details = _get_issue(gh_client, org, repo, issue_num)
        langs = repo_obj.get_languages()
        for k, _ in langs.items():
            details['keywords'].append(k)
        details['title'] = issue_details.title
        details['body'] = issue_details.body
        details['description'] = issue_details.body.replace('\n', '').strip()
        details['state'] = issue_details.state
        if issue_details.state == 'closed':
            details['closed_at'] = issue_details.closed_at.isoformat()
            details['closed_by'] = issue_details.closed_by.name
    except UnknownObjectException:
        return {}
    return details


def get_issue_state(org, repo, issue_num):
    gh_client = github_connect()
    issue_details = _get_issue(gh_client, org, repo, issue_num)
    return issue_details.state


def build_auth_dict():
    """Collect authentication details.

    Returns:
        dict: An authentication dictionary.

    """
    return {
        'api_url': settings.GITHUB_API_BASE_URL,
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET
    }


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
            logger.debug('Validation of date failed.')
            last_validated = None

    # Check whether or not the user's access token has been validated recently.
    if oauth_token and last_validated:
        if (timezone.now() - last_validated) < timedelta(hours=1):
            return True

    _params = build_auth_dict()
    _auth = (_params['client_id'], _params['client_secret'])
    url = TOKEN_URL.format(**_params)
    try:
        response = requests.post(
            url,
            data=json.dumps({'access_token': oauth_token}),
            auth=_auth,
            headers=HEADERS
        )
    except ConnectionError as e:
        if not settings.ENV == 'local':
            logger.error(e)
        else:
            logger.debug(e, '- No connection available. Unable to authenticate with Github.')
        return False

    if response.status_code == 200:
        return True
    return False


def revoke_token(oauth_token):
    """Revoke the specified token."""
    _params = build_auth_dict()
    _auth = (_params['client_id'], _params['client_secret'])
    url = TOKEN_URL.format(**_params)
    response = requests.delete(
        url,
        data=json.dumps({'access_token': oauth_token}),
        auth=_auth,
    )
    if response.status_code == 204:
        return True
    return False


def reset_token(oauth_token):
    """Reset the provided token.

    Args:
        oauth_token (str): The Github OAuth token.

    Returns:
        str: The new Github OAuth token.

    """
    _params = build_auth_dict()
    _auth = (_params['client_id'], _params['client_secret'])
    url = TOKEN_URL.format(**_params)
    response = requests.patch(
        url,
        data=json.dumps({'access_token': oauth_token}),
        auth=_auth,
        headers=HEADERS
    )
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
    github_callback = reverse('social:begin', args=('github',))
    redirect_params = {'next': BASE_URI + redirect_uri}
    redirect_uri = urlencode(redirect_params, quote_via=quote_plus)
    params = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'scope': settings.GITHUB_SCOPE,
        'next': f'{BASE_URI}{github_callback}?{redirect_uri}'
    }
    auth_url = urlencode(params, quote_via=quote_plus)

    return settings.GITHUB_AUTH_BASE_URL + f'?{auth_url}'


def get_github_primary_email(oauth_token):
    """Get the primary email address associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        str: The user's primary github email address.

    """
    try:
        gh_client = github_connect(oauth_token)
        emails = gh_client.get_user().get_emails()
        for email in emails:
            if email.get('primary'):
                return email.get('email', '')
    except Exception as e:
        logger.error(e)

    return ''


def get_github_event_emails(oauth_token, username):
    """Get all email addresses associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        list of str: All of the user's associated emails from github.

    """
    emails = []
    userinfo = get_user(username, oauth_token)
    user_name = userinfo.name if userinfo else None

    try:
        gh_client = github_connect(oauth_token)
        events = _get_user(gh_client, username).get_public_events()
        for event in events:
            payload = event.payload if event.payload else {}
            for commit in payload.get('commits', []):
                author = commit.get('author', {})
                email = author.get('email', '')
                name = author.get('name', '')
                if name and username and user_name:
                    append_email = name.lower() == username.lower() or name.lower() == user_name.lower() \
                                    and email and 'noreply.github.com' not in email
                    if append_email:
                        emails.append(email)
    except GithubException as e:
        logger.error(e)

    return list(set(emails))


def get_github_emails(oauth_token):
    """Get all email addresses associated with the github profile.

    Args:
        oauth_token (str): The Github OAuth2 token to use for authentication.

    Returns:
        list of str: All of the user's associated email from git.

    """
    emails = []
    try:
        gh_client = github_connect(oauth_token)
        email_data = gh_client.get_user().get_emails()

        for email in email_data:
            email_address = email.get('email')
            if email_address and 'noreply.github.com' not in email_address:
                emails.append(email_address)
    except GithubException as e:
        logger.error(e)

    return emails


def get_emails_by_category(username):
    from dashboard.models import Profile
    to_emails = {}
    to_profiles = Profile.objects.filter(handle=username.lower())
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
        return paginated_list[0]
    except IndexError:
        pass
    except Exception as e:
        logger.error(e)
    return {}


def search_users(query, token=None):
    """Search for users on github.

    Args:
        query (str): The query text to match.
        token (str): The user's Github token to be used to perform the search.

    Returns:
        github.PaginatedList: The pygithub paginator object of all results if many True.

    """
    try:
        gh_client = github_connect(token)
        paginated_list = gh_client.search_users(query)
        return paginated_list
    except GithubException as e:
        logger.error(e)
        return []


def get_issue_comments(owner, repo, issue=None, comment_id=None, page=1):
    """Get the comments from issues on a respository.

    Args:
        owner (str): Owner of the repo
        repo (str): Name of the repo
        issue (int): Issue number (optional)
        comment_id (int): Comment ID (optional)
        page (int): Page number (optional)

    Returns:
        github.PaginatedList.PaginatedList / github.IssueComment.IssueComment: The GitHub comments response.

    """
    page -= 1
    if page < 0: page = 0

    gh_client = github_connect()
    paginated_list = []

    try:
        if issue:
            issue = int(issue)
            if comment_id:
                comment_id = int(comment_id)
                issue_comment = _get_issue_comment(gh_client, owner, repo, issue, comment_id)
                return issue_comment
            else:
                paginated_list = _get_issue(gh_client, owner, repo, issue).get_comments().get_page(page)
        else:
            paginated_list = _get_repo(gh_client, repo).get_issues_comments(sort='created', direction='desc').get_page(page)

        return paginated_list
    except Exception as e:
        logger.warn(
            "could not get issues - Reason: %s - owner: %s repo: %s page: %s status_code: %s",
            e.data.get("message"), owner, repo, page, e.status
        )
        return {'status': e.status, 'message': e.data.get("message")}


def get_issues(owner, repo, page=1, state='open'):
    """Get the issues on a respository."""

    page -= 1
    if page < 0: page = 0

    try:
        gh_client = github_connect()
        paginated_list = _get_repo(gh_client, owner, repo).get_issues(
            state=state, sort='created', direction='desc').get_page(page)
        return paginated_list
    except Exception as e:
        logger.warn(
            "could not get issues - Reason: %s - owner: %s repo: %s page: %s state: %s status_code: %s",
            e.data.get("message"), owner, repo, page, state, e.status
        )
    return []


def get_issue_timeline_events(owner, repo, issue, page=1):
    """Get the timeline events for a given issue.

    PLEASE NOTE CURRENT LIMITATION OF 100 EVENTS.
    Args:
        owner (str): Owner of the repo
        repo (str): Name of the repo
        issue (int): Issue number

    Returns:
        github.PaginatedList of githubTimelineEvent: The GitHub timeline response list.
    """
    page -= 1
    if page < 0: page = 0

    gh_client = github_connect()
    try:
        paginated_list = _get_issue(gh_client, owner, issue).get_timeline().get_page(page)
        return paginated_list
    except GithubException as e:
        logger.warn(e)
    return []


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
        actions = [action._rawData for action in actions]
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
                pr_actions = [action._rawData for action in pr_actions]
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


def _get_user(gh_client, user=None):
    """Internal function to retrieve users
    
    This function will attempt to retrieve the user from cache and update it. 
    If that fails, the user will be retreived via API 
    """
    ret = None
    cached_obj = None

    # We only attempt reading from the cache table if a user handle is provided
    if user:
        # We'll attempt to load the users data from the cache, deserialize the data and update it
        try:
            cached_obj = GitCache.get_user(user)
            _temp_object = gh_client.load(BytesIO(cached_obj.data))
            _temp_object.update()
            # Only set ret on the happy path. If anything fails, it is preffered to read the object from GH again.
            ret = _temp_object
        except GitCache.DoesNotExist:
            logger.debug("User not found in cache")
        except Exception:
            logger.warn("Failed to load user from cache", exc_info=True)

    # If no user has been retreived (either no handle or not in cache yet) we get the user
    if not ret:
        ret = gh_client.get_user(user) if user else gh_client.get_user()

    # Cache the data if a user handle is provided
    if user and ret:
        if not cached_obj:
            cached_obj = GitCache(handle=user, category=GitCache.Category.USER)

        user_dump = BytesIO()
        gh_client.dump(ret, user_dump)
        cached_obj.update_data(user_dump.getbuffer())

    return ret


def get_user(user=None, token=None):
    """Get the github user details."""
    try:
        gh_client = github_connect(token)
        return _get_user(gh_client, user)
    except GithubException as e:
        # Do not log exception for github users which are deleted
        if e.data.get("message") != 'Not Found':
            logger.warn(e)

    return None


def get_notifications():
    """Get the Github notifications for Gitcoin Bot."""
    gh_client = github_connect()
    try:
        repo_user = gh_client.get_user()
        paginated_list = repo_user.get_notifications(all=True)
        return paginated_list
    except GithubException as e:
        logger.warn(e)
        return []


def post_issue_comment(owner, repo, issue_num, comment):
    """Post a comment on an issue.

    Args:
        owner (str): Owner of the repo
        repo (str): Name of the repo
        issue_num (int): Issue number
        comment (int): Comment Body

    Returns:
        github.IssueComment.IssueComment: The GitHub created comment.

    """
    gh_client = github_connect()
    try:
        issue_comment = _get_issue(gh_client, owner, repo, issue_num).create_comment(comment)
        return issue_comment
    except GithubException as e:
        logger.warn(e)
        return {}


def patch_issue_comment(issue_id, comment_id, owner, repo, comment):
    """Update a comment on an issue via patch."""
    gh_client = github_connect()
    try:
        issue_comment = _get_issue_comment(gh_client, owner, repo, issue_id, comment_id).edit(comment)
        return issue_comment
    except GithubException as e:
        logger.warn(e)
        return {}


def delete_issue_comment(issue_id, comment_id, owner, repo):
    """Remove a comment on an issue via delete."""
    gh_client = github_connect()
    try:
        issue_comment = _get_issue_comment(gh_client, owner, repo, issue_id, comment_id).delete()
        return issue_comment
    except GithubException as e:
        logger.warn(e)
        return {}


def post_issue_comment_reaction(owner, repo, issue_id, comment_id, content):
    """React to an issue comment."""
    gh_client = github_connect()
    try:
        reaction = _get_issue_comment(gh_client, owner, repo, issue_id, comment_id).create_reaction(content)
        return reaction
    except GithubException as e:
        logger.warn(e)
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
        return {
            'org': org_name(issue_url),
            'repo': repo_name(issue_url),
            'issue_num': int(issue_number(issue_url)) if issue_number(issue_url) else ''
        }


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
    try:
        gh_client = github_connect(token)
        return gh_client.get_rate_limit()
    except GithubException as e:
        logger.warn(e)
        return {}
