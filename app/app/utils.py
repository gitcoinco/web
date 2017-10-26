from django.conf import settings
from dashboard.models import Bounty, Profile
from app.github import get_user
from django.utils import timezone
import requests
import time


def add_contributors(repo_data):
    if repo_data.get('fork', False):
        return repo_data

    from app.github import _auth, headers
    params = {}
    url = repo_data['contributors_url']
    response = requests.get(url, auth=_auth, headers=headers, params=params)
    if response.status_code == 204: #no content
        return repo_data
    rate_limited = type(response.json()) == dict and 'documentation_url' in response.json().keys()
    if rate_limited:
        #retry after rate limit
        time.sleep(60)
        return add_contributors(repo_data)

    # no need for retry
    repo_data['contributors'] = response.json()
    return repo_data

def sync_profile(handle):
    data = get_user(handle)
    is_error = not 'name' in data.keys()
    if is_error:
        print("- error main")
        return

    repos_data = get_user(handle, '/repos')
    repos_data = sorted(repos_data, key=lambda repo: repo['stargazers_count'], reverse=True)
    repos_data = [add_contributors(repo_data) for repo_data in repos_data]

    # store the org info in postgres
    org, _ = Profile.objects.get_or_create(
        handle=handle,
        defaults = {
            'last_sync_date': timezone.now(),
            'data': data,
            'repos_data': repos_data,
        },
        )
    org.handle = handle
    org.data = data
    org.repos_data = repos_data
    org.save()
    print("- updated")
