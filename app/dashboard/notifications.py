# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
'''
    Copyright (C) 2017 Gitcoin Core 

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

'''
from django.conf import settings
import twitter
import requests
from urlparse import urlparse
from app.github import post_issue_comment
from slackclient import SlackClient


def maybe_market_to_twitter(bounty, event_name, txid):

    if not settings.TWITTER_CONSUMER_KEY:
        return False
    if event_name != 'new_bounty':
        return False
    if bounty.get_natural_value() < 0.0001:
        print(bounty)
        print(bounty.pk)
        return False

    api = twitter.Api(
        consumer_key=settings.TWITTER_CONSUMER_KEY,
        consumer_secret=settings.TWITTER_CONSUMER_SECRET,
        access_token_key=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_SECRET,
    )

    new_tweet = "New funded issue worth {} {} \n\n{}".format(
        round(bounty.get_natural_value(), 4),
        bounty.token_name,
        bounty.get_absolute_url()
    )

    try:
        api.PostUpdate(new_tweet)
    except Exception as e:
        print(e)
        return False

    return True


def should_post_in_channel(channel, bounty):
    if channel ['bounties', 'developer']:
        return True
    if 'dev-' in channel:
        keyword = channel.replace('dev-','').lower()
        return keyword in str(bounty.title).lower() \
            or keyword in str(bounty.keywords).lower() \
            or keyword in str(bounty.github_url).lower()

    return False


def maybe_market_to_slack(bounty, event_name, txid):
    if not settings.SLACK_TOKEN:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False

    title = bounty.title if bounty.title else bounty.github_url
    msg = "{} worth {} {}: {} \n\n{}".format(event_name.replace('bounty', 'funded_issue'), round(bounty.get_natural_value(), 4), bounty.token_name, title, bounty.get_absolute_url())

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channels = sc.api_call("channels.list")
        channels = [chan['name'] for chan in channels['channels']]
        channels_to_post_in = [channel for channel in channels if should_post_in_channel(channel, bounty)]
        channel = 'bounties'
        for channel in channels_to_post_in:
            sc.api_call(
              "chat.postMessage",
              channel=channel,
              text=msg,
            ) 
    except:
        return False       

    return True


def maybe_market_tip_to_slack(tip, event_name, txid):
    if not settings.SLACK_TOKEN:
        return False

    title = tip.github_url
    msg = "{} worth {} {}: {} \n\n{}".format(event_name, round(tip.amount, 4), tip.tokenName, title, tip.github_url)

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channel = 'bounties'
        sc.api_call(
          "chat.postMessage",
          channel=channel,
          text=msg,
        )
    except Exception as e:
        print(e)
        return False

    return True


def maybe_market_to_github(bounty, event_name, txid):
    if not settings.GITHUB_CLIENT_ID:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False

    # prepare message
    msg = ''
    if event_name == 'new_bounty':
        usdt_value = "(" + str(round(bounty.value_in_usdt, 2)) + " USDT)" if bounty.value_in_usdt else ""
        msg = "__This issue now has a funding of {} {} {} attached to it.__  To view or claim this funding, [click here]({}).".format(round(bounty.get_natural_value(), 4), bounty.token_name, usdt_value, bounty.get_absolute_url())
    elif event_name == 'approved_claim':
        msg = "__The funding of {} {} attached to this issue has been approved & issued.__  \n\nLearn more at: {}".format(round(bounty.get_natural_value(), 4), bounty.token_name, bounty.get_absolute_url())
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


def maybe_market_tip_to_github(tip):
    if not settings.GITHUB_CLIENT_ID:
        return False
    if not tip.github_url:
        return False

    # prepare message
    username = tip.username if '@' in tip.username else str('@' + tip.username)
    _from = " from {}".format(tip.from_name) if tip.from_name else ""
    warning = tip.network if tip.network != 'mainnet' else ""
    msg = "⚡️ A tip worth {} {} {} has been granted to {} for this issue{}. ⚡️ \n\nNice work {}, check your email for further instructions. | <a href='https://gitcoin.co/tip'>Send a Tip</a>".format(round(tip.amount, 3), warning, tip.tokenName, username, _from, username)

    # actually post
    url = tip.github_url
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
    from marketing.mails import new_bounty_claim, new_bounty_rejection, new_bounty_acceptance

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
            new_bounty_acceptance(b, to_emails)
        except Exception as e:
            print(e)
    if event_name == 'rejected_claim':
        try:
            to_emails = [b.bounty_owner_email, b.claimee_email]
            new_bounty_rejection(b, to_emails)
        except Exception as e:
            print(e)

    return len(to_emails)

