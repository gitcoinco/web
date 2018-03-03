"""
Methods for interacting with the Github API as a Github App
"""
import datetime
import json
import re

from django.conf import settings

import jwt
import requests
from github.utils import post_issue_comment, post_issue_comment_reaction

GITCOINBOT_APP_ID = settings.GITCOINBOT_APP_ID
SECRET_KEYSTRING = settings.SECRET_KEYSTRING


def help_text():
    help_text_response = "I am @{}, a bot that facilitates gitcoin bounties.\n".format(settings.GITHUB_API_USER) + \
    "\n" +\
    "<hr>" +\
    "Here are the commands I understand:\n" +\
    "\n" +\
    " * `bounty <amount> ETH` -- receive link to gitcoin.co form to create bounty.\n" +\
    " * `claim` -- receive link to gitcoin.co to start work on a bounty.\n" +\
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
    bounty_link = "{}funding/new?source={}&amount={}".format(
        settings.BASE_URL, issue_link, bounty_amount)
    new_bounty_response = "To create the bounty please [visit this link]({}).\n".format(bounty_link) +\
    "\n PS Make sure you're logged in to Metamask!"
    return new_bounty_response

def parse_comment_amount(comment_text):
    re_amount = r'\d*\.?\d+'
    result = re.findall(re_amount, comment_text)
    return result[0]

def parse_tippee_username(comment_text):
    re_username = r'[@][a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}'
    username = re.findall(re_username, comment_text)
    return username[-1]

def new_tip_text(owner, repo, issue_id, comment_text):
    tip_amount = parse_comment_amount(comment_text)
    username = parse_tippee_username(comment_text)
    issue_url = "https://github.com/{}/{}/issues/{}".format(owner,
                                                            repo,
                                                            issue_id)
    tip_link = '{}tip/?amount={}&username={}&source={}'.format(
        settings.BASE_URL, tip_amount, username, issue_url)
    tip_response = 'To complete the tip, please [visit this link]({}).'.format(
        tip_link) + "\n PS Make sure you're logged in to Metamask!"
    return tip_response

def claim_bounty_text(owner, repo, issue_id):
    issue_url = "https://github.com/{}/{}/issues/{}".format(owner,
                                                            repo,
                                                            issue_id)
    claim_link = '{}funding/details/?url={}'.format(
        settings.BASE_URL, issue_url)
    claim_response = 'To finish claiming this bounty please [visit this link]({})'.format(
        claim_link)
    return claim_response

def confused_text():
    return 'Sorry I did not understand that request. Please try again'

def post_gitcoin_app_comment(owner, repo, issue_id, content, install_id):
    token = create_token(install_id)
    url = 'https://api.github.com/repos/{}/{}/issues/{}/comments'.format(
        owner, repo, issue_id)
    github_app_headers = {
        'Authorization': 'token ' + token,
        'Accept': 'application/vnd.github.machine-man-preview+json'
    }
    body = {
        'body': content
    }

    response = requests.post(url, data=json.dumps(body), headers=github_app_headers)
    return response.json

def create_token(install_id):
    # Token expires after 10 minutes
    payload = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=500),
        'iss': GITCOINBOT_APP_ID}
    jwt_token = jwt.encode(payload, SECRET_KEYSTRING, algorithm='RS256')
    jwt_token_string = jwt_token.decode('utf-8')
    url = 'https://api.github.com/installations/{}/access_tokens'.format(install_id)
    github_app_headers = {
        'Authorization': 'Bearer ' + jwt_token_string,
        'Accept': 'application/vnd.github.machine-man-preview+json'}
    response = requests.post(url, headers=github_app_headers)
    token = json.loads(response.content)['token']
    return token

def determine_response(owner, repo, comment_id, comment_text, issue_id, install_id):
    help_regex = r'@?[Gg]itcoinbot\s[Hh]elp'
    bounty_regex = r'@?[Gg]itcoinbot\s[Bb]ounty\s\d*\.?(\d+\s?)'
    claim_regex = r'@?[Gg]itcoinbot\s[Cc]laim'
    tip_regex = r'@?[Gg]itcoinbot\s[Tt]ip\s@\w*\s\d*\.?(\d+\s?)'

    if re.match(help_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        post_gitcoin_app_comment(owner, repo, issue_id, help_text(), install_id)
    elif re.match(bounty_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        bounty_text = new_bounty_text(owner, repo, issue_id, comment_text)
        post_gitcoin_app_comment(owner, repo, issue_id, bounty_text, install_id)
    elif re.match(claim_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        claim_text = claim_bounty_text(owner, repo, issue_id)
        post_gitcoin_app_comment(owner, repo, issue_id, claim_text, install_id)
    elif re.match(tip_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, 'heart')
        tip_text = new_tip_text(owner, repo, issue_id, comment_text)
        post_gitcoin_app_comment(owner, repo, issue_id, tip_text, install_id)
    else:
        post_issue_comment_reaction(owner, repo, comment_id, 'confused')
        post_gitcoin_app_comment(owner, repo, issue_id, confused_text(),install_id)
