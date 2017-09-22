from requests_oauthlib import OAuth2Session
from django.conf import settings


def get_github_user_profile(token):

    github = OAuth2Session(
        settings.GITHUB_CLIENT_ID,
        token=token,
    )

    creds = github.get('https://api.github.com/user').json()
    print(creds)
    return creds
