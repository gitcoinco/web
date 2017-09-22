from django.conf import settings
import requests
import json


_auth = (settings.GITHUB_API_USER, settings.GITHUB_API_TOKEN)
headers = {
    'Accept': 'application/vnd.github.squirrel-girl-preview'
}


class GitHubAPI():

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

