'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from django.conf import settings
import requests
import json


_auth = (settings.GITHUB_API_USER, settings.GITHUB_API_TOKEN)
headers = {
    'Accept': 'application/vnd.github.squirrel-girl-preview'
}


def get_issue_comments(owner, repo):
    params = {
        'sort': 'created',
        'direction': 'desc',
    }
    url = 'https://api.github.com/repos/{}/{}/issues/comments'.format(owner, repo)
    response = requests.get(url, auth=_auth, headers=headers, params=params)

    return response.json()


def get_user(user):
    url = 'https://api.github.com/users/{}'.format(user)
    response = requests.get(url, auth=_auth, headers=headers)

    return response.json()


def post_issue_comment(owner, repo, issue_num, comment):

    url = 'https://api.github.com/repos/{}/{}/issues/{}/comments'.format(owner, repo, issue_num)
    body = {
        'body': comment,
    }
    response = requests.post(url, data=json.dumps(body), auth=_auth)
    return response.json()


def post_issue_comment_reaction(owner, repo, comment_id, content):
    url = 'https://api.github.com/repos/{}/{}/issues/comments/{}/reactions'.format(owner, repo, comment_id)
    body = {
        'content': content,
    }
    response = requests.post(url, data=json.dumps(body), auth=_auth, headers=headers)
    return response.json()

