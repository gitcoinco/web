'''
Methods for interacting with the Github API
'''
from django.conf import settings

import datetime
import json
import jwt
import requests
import re

_auth = (settings.GITHUB_API_USER, settings.GITHUB_API_TOKEN)
GITCOINBOT_APP_ID = settings.GITCOINBOT_APP_ID
SECRET_KEYSTRING = settings.SECRET_KEYSTRING

headers = {
    'Accept': 'application/vnd.github.squirrel-girl-preview'
}

v3headers = {
    'Accept': 'application/vnd.github.v3.text-match+json'
}

githubAppHeaders= {
    'Accept': 'application/vnd.github.machine-man-preview+json'
}


def help_text():
    help_text_response = "I am @{}, a bot that facilitates gitcoin bounties.\n".format(settings.GITHUB_API_USER) + \
        "\n" +\
        "<hr>" +\
        "Here are the commands I understand:\n" +\
        "\n" +\
        " * `bounty <amount> ETH` -- receive link to gitcoin.co form to create bounty.\n" +\
        " * `claim` -- receive link to gitcoin.co to claim bounty.\n" +\
        " * `approve` -- receive link to gitcoin.co to approve bounty.\n" +\
        " * `tip <user> <amount> ETH` -- receive link to complete tippping another github user *<amount>* ETH.\n" +\
        " * `help` -- displays a help menu\n" +\
        "\n" +\
        "<br>" +\
        "Learn more at: [https://gitcoin.co](https://gitcoin.co)\n" +\
        ":zap::heart:, {}\n".format("@" + settings.GITHUB_API_USER)
    return help_text_response


def new_bounty_text(owner, repo, issue_id, comment_text):
    issue_link = "https://github.com/{}/{}/issues/{}".format(owner,
                                                            repo,
                                                            issue_id )
    bounty_amount = parse_comment_amount(comment_text)
    # prod
    # bounty_link = "https://gitcoin.co/funding/new?source={}&amount={}".format(
    #     issue_link, bounty_amount
    # )
    #dev
    bounty_link = "http://localhost:8000/funding/new?source={}&amount={}".format(
        issue_link, bounty_amount
    )

    new_bounty_response = "To create the bounty please [visit this link]({}).\n".format(bounty_link) +\
    "\n" +\
    "PS Make sure you're logged in to Metamask!"
    return new_bounty_response


def parse_comment_amount(comment_text):
    re_amount = '\d+\.?\d+'
    result = re.findall(re_amount, comment_text)

    return result[0]

def tip_text():
    # TODO Need to make the url have params that can autofill the form
    tip_response = "To complete the tip, please [visit this link]({}).".format(
        'https://gitcoin.co/tip')
    return tip_response


def confused_text():
    response = "Sorry I did not understand that request. Please try again"
    return response


def post_issue_comment(owner, repo, issue_id, comment):
    url = 'https://api.github.com/repos/{}/{}/issues/{}/comments'.format(
        owner, repo, issue_id)
    body = {
        'body': comment,
    }
    response = requests.post(url, data=json.dumps(body), auth=_auth)
    return response.json()


def post_issue_comment_reaction(owner, repo, comment_id, content):
    url = 'https://api.github.com/repos/{}/{}/issues/comments/{}/reactions'.format(
        owner, repo, comment_id)
    body = {
        'content': content,
    }
    response = requests.post(url, data=json.dumps(
        body), auth=_auth, headers=headers)
    print('reacting with a heart')
    print(response.json())
    return response.json()

def create_token():
    # Token expires after 10 minutes
    payload = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=600),
        'iss': GITCOINBOT_APP_ID
    }
    token = jwt.encode(payload, SECRET_KEYSTRING, algorithm='RS256')
    return token

def determine_response(owner, repo, comment_id, comment_text, issue_id):
    help_regex = '@?[Gg]itcoinbot\s[Hh]elp'
    bounty_regex = '@?[Gg]itcoinbot\s[Bb]ounty\s\d*\.?(\d+\s?)'
    claim_regex = '@?[Gg]itcoinbot\s[Cc]laim'
    approve_regex = '@?[Gg]itcoinbot\s[Aa]pprove'
    tip_regex = '@?[Gg]itcoinbot\s[Tt]ip\s@\w*\s\d*\.?(\d+\s?)'

    if re.match(help_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        post_issue_comment(owner, repo, issue_id, help_text())
    elif re.match(bounty_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        bounty_text = new_bounty_text(owner, repo, issue_id, comment_text)
        post_issue_comment(owner, repo, issue_id, bounty_text)
    elif re.match(claim_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        pass
    elif re.match(approve_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, 'hooray')
        pass
    elif re.match(tip_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, 'heart')
        post_issue_comment(owner, repo, issue_id, tip_text())
    else:
        pass
        # Make sure to not respond after gitcoinbot comments...
        # post_issue_comment_reaction(owner, repo, comment_id, 'confused')
        # post_issue_comment(owner, repo, issue_id, tip_text())

    # TODO run a pip freeze to update the dependencies aka PyJWT and cryptography