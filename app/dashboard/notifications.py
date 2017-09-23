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
import twitter
import requests
from urlparse import urlparse
from app.github import post_issue_comment
from marketing.mail import new_bounty_claim, new_bounty_rejection, new_bounty_acceptance


def maybe_market_to_twitter(bounty, event_name, txid):

    if not settings.TWITTER_CONSUMER_KEY:
        return False
    if event_name != 'new_bounty':
        return False

    api = twitter.Api(
        consumer_key=settings.TWITTER_CONSUMER_KEY,
        consumer_secret=settings.TWITTER_CONSUMER_SECRET,
        access_token_key=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_SECRET,
    )

    new_tweet = "New bounty worth {} {} \n\n{}".format(
        round(bounty.get_natural_value(), 2),
        bounty.token_name,
        bounty.get_absolute_url()
    )

    try:
        api.PostUpdate(new_tweet)
    except Exception as e:
        print(e)
        return False

    return True


def maybe_market_to_slack(bounty, event_name, txid):
    if not settings.TWITTER_CONSUMER_KEY:
        return False

    title = bounty.title if bounty.title else bounty.github_url
    msg = "{} worth {} {}: {} \n\n{}".format(event_name, round(bounty.get_natural_value(), 2), bounty.token_name, title, bounty.get_absolute_url())

    payload = {
        "text": msg,
    }
    try:
        r = requests.post(
            settings.SLACK_WEBHOOK,
            json=payload,
            timeout=3)
        return r.status_code == 200
    except Exception as e:
        print(e)
        return False

    pass


def maybe_market_to_github(bounty, event_name, txid):
    if not settings.GITHUB_CLIENT_ID:
        return False

    # prepare message
    msg = ''
    if event_name == 'new_bounty':
        msg = "__This issue now has a bounty of {} {} attached to it.__  \n\nLearn more at: {}".format(round(bounty.get_natural_value(), 2), bounty.token_name, bounty.get_absolute_url())
    elif event_name == 'approved_claim':
        msg = "__The bounty of {} {} attached to this issue has been approved & issue.d__  \n\nLearn more at: {}".format(round(bounty.get_natural_value(), 2), bounty.token_name, bounty.get_absolute_url())
    else:
        return False

    # actually post
    url = bounty.github_url
    uri = urlparse(url).path
    uri_array = uri.split('/')
    try:
        username = uri_array[1]
        repo = uri_array[2]
        issue_num = uri_array[4]

        post_issue_comment(username, repo, issue_num, msg)

    except Exception as e:
        print(e)
        return False

    return True


def maybe_market_to_email(b, event_name, txid):

    #TODO: allow people to subscribe to new_bounty notifications
    #new_bounty(b, [to_email])

    to_emails = []

    if event_name == 'new_claim':
        try:
            to_emails = [b.bounty_owner_email]
            new_bounty_claim(b, to_emails)
        except Exception as e:
            print(e)
    if event_name == 'approved_claim':
        try:
            to_emails = [b.bounty_owner_email, b.claimee_email]
            new_bounty_rejection(b, to_emails)
        except Exception as e:
            print(e)
    if event_name == 'rejected_claim':
        try:
            to_emails = [b.bounty_owner_email, b.claimee_email]
            new_bounty_acceptance(b, to_emails)
        except Exception as e:
            print(e)

    return len(to_emails)

