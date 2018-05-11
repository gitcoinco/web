# -*- coding: utf-8 -*-
"""Handle dashboard related notifications.

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
import logging
import random
import re
import sys
from urllib.parse import urlparse as parse

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime

import rollbar
import twitter
from economy.utils import convert_token_to_usdt
from github.utils import delete_issue_comment, org_name, patch_issue_comment, post_issue_comment, repo_name
from marketing.mails import tip_email
from marketing.models import GithubOrgToTwitterHandleMapping
from pyshorteners import Shortener
from slackclient import SlackClient


def github_org_to_twitter_tags(github_org):
    """Build a string of github organization twitter tags.

    Args:
        github_org (str): The Github organization.

    Returns:
        str: The concatenated string of twitter tags.

    """
    twitter_handles = GithubOrgToTwitterHandleMapping.objects.filter(github_orgname__iexact=github_org)
    twitter_handles = twitter_handles.values_list('twitter_handle', flat=True)
    twitter_tags = " ".join([f"@{ele}" for ele in twitter_handles])
    return twitter_tags


def maybe_market_to_twitter(bounty, event_name):
    """Tweet the specified Bounty event.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.

    Returns:
        bool: Whether or not the twitter notification was sent successfully.

    """
    if not settings.TWITTER_CONSUMER_KEY:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    api = twitter.Api(
        consumer_key=settings.TWITTER_CONSUMER_KEY,
        consumer_secret=settings.TWITTER_CONSUMER_SECRET,
        access_token_key=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_SECRET,
    )
    tweet_txts = [
        "Earn {} {} {} now by completing this task: \n\n{}",
        "Oppy to earn {} {} {} for completing this task: \n\n{}",
        "Is today the day you (a) boost your OSS rep (b) make some extra cash? 🤔 {} {} {} \n\n{}",
    ]
    if event_name == 'remarket_bounty':
        tweet_txts = tweet_txts + [
            "Gitcoin open task of the day is worth {} {} {} ⚡️ \n\n{}",
            "Task of the day 💰 {} {} {} ⚡️ \n\n{}",
        ]
    elif event_name == 'new_bounty':
        tweet_txts = tweet_txts + [
            "Extra! Extra 🗞🗞 New Funded Issue, Read all about it 👇  {} {} {} \n\n{}",
            "Hot off the blockchain! 🔥🔥🔥 There's a new task worth {} {} {} \n\n{}",
            "💰 New Task Alert.. 💰 Earn {} {} {} for working on this 👇 \n\n{}",
        ]
    elif event_name == 'increase_payout':
        tweet_txts = [
            'Increased Payout on {} {} {}\n{}'
        ]
    elif event_name == 'start_work':
        tweet_txts = [
            'Work started on {} {} {}\n{}'
        ]
    elif event_name == 'stop_work':
        tweet_txts = [
            'Work stopped on {} {} {}\n{}'
        ]
    elif event_name == 'work_done':
        tweet_txts = [
            'Work done on {} {} {}\n{}'
        ]
    elif event_name == 'work_submitted':
        tweet_txts = [
            'Work submitted on {} {} {}\n{}'
        ]
    elif event_name == 'killed_bounty':
        tweet_txts = [
            'Bounty killed on {} {} {}\n{}'
        ]

    random.shuffle(tweet_txts)
    tweet_txt = tweet_txts[0]

    url = bounty.get_absolute_url()
    is_short = False
    for shortener in ['Tinyurl', 'Adfly', 'Isgd', 'QrCx']:
        try:
            if not is_short:
                shortener = Shortener(shortener)
                response = shortener.short(url)
                if response != 'Error' and 'http' in response:
                    url = response
                is_short = True
        except Exception:
            pass

    new_tweet = tweet_txt.format(
        round(bounty.get_natural_value(), 4),
        bounty.token_name,
        f"({bounty.value_in_usdt_now} USD @ ${round(convert_token_to_usdt(bounty.token_name),2)}/{bounty.token_name})" if bounty.value_in_usdt_now else "",
        url
    )
    new_tweet = new_tweet + " " + github_org_to_twitter_tags(bounty.org_name)  # twitter tags
    if bounty.keywords:  # hashtags
        for keyword in bounty.keywords.split(','):
            _new_tweet = new_tweet + " #" + str(keyword).lower().strip()
            if len(_new_tweet) < 140:
                new_tweet = _new_tweet

    try:
        api.PostUpdate(new_tweet)
    except Exception as e:
        print(e)
        return False
    return True


def maybe_market_to_slack(bounty, event_name):
    """Send a Slack message for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.

    Returns:
        bool: Whether or not the Slack notification was sent successfully.

    """
    if not settings.SLACK_TOKEN:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    msg = build_message_for_slack(bounty, event_name)
    if not msg:
        return False

    try:
        channel = 'notif-gitcoin'
        sc = SlackClient(settings.SLACK_TOKEN)
        sc.api_call("chat.postMessage", channel=channel, text=msg)
    except Exception as e:
        print(e)
        return False
    return True


def build_message_for_slack(bounty, event_name):
    """Build message to be posted to slack.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.

    Returns:
        str: Message to post to slack.

    """
    conv_details = ""
    usdt_details = ""
    try:
        conv_details = f"@ (${round(convert_token_to_usdt(bounty.token_name),2)}/{bounty.token_name})"
        usdt_details = f"({bounty.value_in_usdt_now} USD {conv_details} "
    except Exception:
        pass  # no USD conversion rate

    title = bounty.title if bounty.title else bounty.github_url
    msg = f"{event_name.replace('bounty', 'funded_issue')} worth {round(bounty.get_natural_value(), 4)} {bounty.token_name} " \
          f"{usdt_details}" \
          f"{bounty.token_name}: {title} \n\n{bounty.get_absolute_url()}"
    return msg


def maybe_market_to_user_slack(bounty, event_name):
    """Send a Slack message to the user's slack channel for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.

    Returns:
        bool: Whether or not the Slack notification was sent successfully.

    """
    from dashboard.models import Profile
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    msg = build_message_for_slack(bounty, event_name)
    if not msg:
        return False

    url = bounty.github_url
    sent = False
    try:
        repo = org_name(url) + '/' + repo_name(url)
        subscribers = Profile.objects.filter(slack_repos__contains=[repo])
        subscribers = subscribers & Profile.objects.exclude(slack_token='', slack_channel='')
        for subscriber in subscribers:
            try:
                sc = SlackClient(subscriber.slack_token)
                sc.api_call("chat.postMessage", channel=subscriber.slack_channel, text=msg)
                sent = True
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

    return sent


def maybe_market_tip_to_email(tip, emails):
    """Send an email for the specified Tip.

    Args:
        tip (dashboard.models.Tip): The Tip to be marketed.
        emails (list of str): The list of emails to notify.

    Returns:
        bool: Whether or not the email notification was sent successfully.

    """
    if tip.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    tip_email(tip, set(emails), True)
    return True


def maybe_market_tip_to_slack(tip, event_name):
    """Send a Slack message for the specified Tip.

    Args:
        tip (dashboard.models.Tip): The Tip to be marketed.
        event_name (str): The name of the event.

    Returns:
        bool: Whether or not the Slack notification was sent successfully.

    """
    if not settings.SLACK_TOKEN or (tip.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
        return False

    title = tip.github_url
    msg = f"{event_name} worth {round(tip.amount, 4)} {tip.tokenName}: {title} \n\n{tip.github_url}"

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channel = 'notif-gitcoin'
        sc.api_call("chat.postMessage", channel=channel, text=msg)
    except Exception as e:
        print(e)
        return False
    return True


def get_status_header(bounty):
    statuses = ['Open']
    status = bounty.status
    if status == 'unknown':
        return ""
    elif status == 'cancelled':
        statuses.append('**Cancelled**')
    elif status == 'expired':
        statuses.append('**Expired**')
    else:
        if status == 'open':
            statuses = ['**Open**', 'Started', 'Submitted', 'Done']
        elif status == 'started':
            statuses += ['**Started**', 'Submitted', 'Done']
        else:
            statuses.append('Started')
            if status == 'submitted':
                statuses += ['**Submitted**', 'Done']
            else:
                statuses.append('Submitted')
                if status == 'done':
                    statuses.append('**Done**')
                else:
                    statuses.append('**Done**')

    # 1. Open | **2. Started** | 3. Submitted | 4. Done
    status_bar = ""
    for x, status in enumerate(statuses):
        status_bar += f"{x+1}. {status} "

    return f"Issue Status: {status_bar}\n\n<hr>\n\n"


def build_github_notification(bounty, event_name, profile_pairs=None):
    """Build a Github comment for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.
        profile_pairs (list of tuples): The list of username and profile page
            URL tuple pairs.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    from dashboard.models import BountyFulfillment, Interest
    msg = ''
    usdt_value = ""
    try:
        usdt_value = f"({round(bounty.value_in_usdt_now, 2)} USD @ ${round(convert_token_to_usdt(bounty.token_name), 2)}/{bounty.token_name})" if bounty.value_in_usdt_now else ""
    except Exception:
        pass  # no USD conversion rate available
    natural_value = round(bounty.get_natural_value(), 4)
    absolute_url = bounty.get_absolute_url()
    amount_open_work = "{:,}".format(amount_usdt_open_work())
    profiles = ""
    bounty_owner = f"@{bounty.bounty_owner_github_username}" if bounty.bounty_owner_github_username else ""
    status_header = get_status_header(bounty)

    if profile_pairs:
        from dashboard.utils import get_ordinal_repr  # hack for circular import issue
        for i, profile in enumerate(profile_pairs, start=1):
            show_dibs = event_name == 'work_started' and len(profile_pairs) > 1
            dibs = f" ({get_ordinal_repr(i)} precedence)" if show_dibs else ""
            profiles = profiles + f"\n {i}. [@{profile[0]}]({profile[1]}) {dibs}"
        profiles += "\n\n"
    if event_name == 'new_bounty':
        msg = f"{status_header}__This issue now has a funding of {natural_value} " \
              f"{bounty.token_name} {usdt_value} attached to it.__\n\n * If you would " \
              f"like to work on this issue you can 'start work' [on the Gitcoin Issue Details page]({absolute_url}).\n " \
              "* Questions? Checkout <a href='https://gitcoin.co/help'>Gitcoin Help</a> or the " \
              f"<a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${amount_open_work}" \
              " more funded OSS Work available on the [Gitcoin Issue Explorer](https://gitcoin.co/explorer)\n"
    if event_name == 'increased_bounty':
        msg = f"{status_header}__The funding of this issue was increased to {natural_value} " \
              f"{bounty.token_name} {usdt_value}.__\n\n * If you would " \
              f"like to work on this issue you can claim it [here]({absolute_url}).\n " \
              "* If you've completed this issue and want to claim the bounty you can do so " \
              f"[here]({absolute_url})\n * Questions? Checkout <a href='https://gitcoin.co/help'>Gitcoin Help</a> or " \
              f"the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${amount_open_work}" \
              " more funded OSS Work available on the [Gitcoin Issue Explorer](https://gitcoin.co/explorer)\n"
    elif event_name == 'killed_bounty':
        msg = f"{status_header}__The funding of {natural_value} {bounty.token_name} " \
              f"{usdt_value} attached to this issue has been **cancelled** by the bounty submitter__\n\n " \
              "* Questions? Checkout <a href='https://gitcoin.co/help'>Gitcoin Help</a> or the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * " \
              f"${amount_open_work} more funded OSS Work available on the [Gitcoin Issue Explorer](https://gitcoin.co/explorer)\n"
    elif event_name == 'rejected_claim':
        msg = f"{status_header}__The work submission for {natural_value} {bounty.token_name} {usdt_value} " \
              "has been **rejected** and can now be submitted by someone else.__\n\n * If you would " \
              f"like to work on this issue you can claim it [here]({absolute_url}).\n * If you've " \
              f"completed this issue and want to claim the bounty you can do so [here]({absolute_url})\n " \
              "* Questions? Checkout <a href='https://gitcoin.co/help'>Gitcoin Help</a> or <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * " \
              f"${amount_open_work} more funded OSS Work available on the [Gitcoin Issue Explorer](https://gitcoin.co/explorer)\n"
    elif event_name == 'work_started':
        from_now = naturaltime(bounty.expires_date)
        msg = f"{status_header}__Work has been started__.\n{profiles} has committed to working on this project to be " \
              f"completed {from_now}.\n\n"
        bounty_owner_clear = f"@{bounty.bounty_owner_github_username}" if bounty.bounty_owner_github_username else ""
        try:
            if profile_pairs:
                for profile in profile_pairs:
                    interests = Interest.objects.filter(profile__handle=profile[0], bounty=bounty)
                    for interest in interests:
                        if interest.issue_message.strip():
                            msg += f"\n__Please answer following questions/comments__ {bounty_owner_clear}:\n\n" + \
                                    interest.issue_message
        except Exception as e:
            print(e)
    elif event_name == 'work_submitted':
        sub_msg = ""
        if bounty.fulfillments.exists():
            sub_msg = f"\n\n{bounty_owner if bounty_owner else 'If you are the bounty funder,'} " \
                       "please take a look at the submitted work:\n"
            for bf in bounty.fulfillments.all():
                username = "@"+bf.fulfiller_github_username if bf.fulfiller_github_username else bf.fulfiller_address
                link_to_work = f"[PR]({bf.fulfiller_github_url})" if bf.fulfiller_github_url else "(Link Not Provided)"
                sub_msg += f"* {link_to_work} by {username}\n"

        msg = f"{status_header}__Work for {natural_value} {bounty.token_name} {usdt_value} has been submitted by__:\n" \
              f"{profiles}{sub_msg}\n<hr>\n\n* Learn more [on the Gitcoin Issue Details page]({absolute_url})\n" \
              "* Questions? Checkout <a href='https://gitcoin.co/help'>Gitcoin Help</a> or the " \
              f"<a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n${amount_open_work} more funded " \
              "OSS Work available on the [Gitcoin Issue Explorer](https://gitcoin.co/explorer)\n"
    elif event_name == 'work_done':
        try:
            accepted_fulfillment = bounty.fulfillments.filter(accepted=True).latest('fulfillment_id')
            accepted_fulfiller = f' to @{accepted_fulfillment.fulfiller_github_username}'
        except BountyFulfillment.DoesNotExist:
            accepted_fulfiller = ''

        msg = f"{status_header}__The funding of {natural_value} {bounty.token_name} {usdt_value} attached to this " \
              f"issue has been approved & issued{accepted_fulfiller}.__  \n\n * Learn more at [on the Gitcoin " \
              f"Issue Details page]({absolute_url})\n * Questions? Checkout <a href='https://gitcoin.co/help'>Gitcoin Help</a> or the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>" \
              f"\n * ${amount_open_work} more funded OSS Work available on the [Gitcoin Issue Explorer](https://gitcoin.co/explorer)\n"
    return msg


def maybe_market_to_github(bounty, event_name, profile_pairs=None):
    """Post a Github comment for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.
        profile_pairs (list of tuples): The list of username and profile page
            URL tuple pairs.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    if (not settings.GITHUB_CLIENT_ID) or (bounty.get_natural_value() < 0.0001) or (
       bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
        return False

    # Define posting specific variables.
    comment_id = None
    url = bounty.github_url
    uri = parse(url).path
    uri_array = uri.split('/')

    # Prepare the comment message string.
    msg = build_github_notification(bounty, event_name, profile_pairs)
    if not msg:
        return False

    try:
        username = uri_array[1]
        repo = uri_array[2]
        issue_num = uri_array[4]

        if event_name == 'work_started':
            comment_id = bounty.interested_comment
        elif event_name in ['work_done', 'work_submitted']:
            comment_id = bounty.submissions_comment

        # Handle creating or updating comments if profiles are provided.
        if event_name in ['work_started', 'work_submitted'] and profile_pairs:
            if comment_id is not None:
                patch_issue_comment(comment_id, username, repo, msg)
            else:
                response = post_issue_comment(username, repo, issue_num, msg)
                if response.get('id'):
                    if event_name == 'work_started':
                        bounty.interested_comment = int(response.get('id'))
                    elif event_name in ['work_done', 'work_submitted']:
                        bounty.submissions_comment = int(response.get('id'))
                    bounty.save()
        # Handle deleting comments if no profiles are provided.
        elif event_name in ['work_started'] and not profile_pairs:
            if comment_id:
                delete_issue_comment(comment_id, username, repo)
                if event_name == 'work_started':
                    bounty.interested_comment = None
                elif event_name == 'work_done':
                    bounty.submissions_comment = None
                bounty.save()
        # If this isn't work_started/done, simply post the issue comment.
        else:
            post_issue_comment(username, repo, issue_num, msg)
    except IndexError:
        return False
    except Exception as e:
        extra_data = {'github_url': url, 'bounty_id': bounty.pk, 'event_name': event_name}
        rollbar.report_exc_info(sys.exc_info(), extra_data=extra_data)
        print(e)
        return False
    return True


def amount_usdt_open_work():
    """Get the amount in USDT of all current open and submitted work.

    Returns:
        float: The sum of all USDT values rounded to the nearest 2 decimals.

    """
    from dashboard.models import Bounty
    bounties = Bounty.objects.filter(network='mainnet', current_bounty=True, idx_status__in=['open', 'submitted'])
    return round(sum([b.value_in_usdt_now for b in bounties if b.value_in_usdt_now]), 2)


def maybe_market_tip_to_github(tip):
    """Post a Github comment for the specified Tip.

    Args:
        tip (dashboard.models.Tip): The Tip to be marketed.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    if (not settings.GITHUB_CLIENT_ID) or (not tip.github_url) or (
       tip.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
        return False

    # prepare message
    username = tip.username if '@' in tip.username else f'@{tip.username}'
    _from = f" from {tip.from_name}" if tip.from_name else ""
    warning = tip.network if tip.network != 'mainnet' else ""
    _comments = "\n\nThe sender had the following public comments: \n> " \
                f"{tip.comments_public}" if tip.comments_public else ""
    try:
        value_in_usd = f"({tip.value_in_usdt_now} USD @ ${round(convert_token_to_usdt(tip.tokenName), 2)}/{tip.tokenName})" if tip.value_in_usdt_now else ""
    except Exception:
        pass  # no USD conv rate
    msg = f"⚡️ A tip worth {round(tip.amount, 5)} {warning} {tip.tokenName} {value_in_usd} has been " \
          f"granted to {username} for this issue{_from}. ⚡️ {_comments}\n\nNice work {username}! To " \
          "redeem your tip, login to Gitcoin at https://gitcoin.co/explorer and select 'Claim Tip' " \
          "from dropdown menu in the top right, or check your email for a link to the tip redemption " \
          f"page. \n\n * ${amount_usdt_open_work()} in Funded OSS Work Available at: " \
          "https://gitcoin.co/explorer\n * Incentivize contributions to your repo: " \
          "<a href='https://gitcoin.co/tip'>Send a Tip</a> or <a href='https://gitcoin.co/funding/new'>" \
          "Fund a PR</a>\n * No Email? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>"

    # actually post
    url = tip.github_url
    uri = parse(url).path
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


def maybe_market_to_email(b, event_name):
    from marketing.mails import new_work_submission, new_bounty_rejection, new_bounty_acceptance
    to_emails = []
    if b.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    if event_name == 'new_bounty' and not settings.DEBUG:
        # handled in 'new_bounties_email'
        return
    elif event_name == 'work_submitted':
        try:
            to_emails = [b.bounty_owner_email]
            new_work_submission(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)
    elif event_name == 'work_done':
        try:
            accepted_fulfillment = b.fulfillments.filter(accepted=True).latest('modified_on')
            to_emails = [b.bounty_owner_email, accepted_fulfillment.fulfiller_email]
            new_bounty_acceptance(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)
    elif event_name == 'rejected_claim':
        try:
            rejected_fulfillment = b.fulfillments.filter(accepted=False).latest('modified_on')
            to_emails = [b.bounty_owner_email, rejected_fulfillment.fulfiller_email]
            new_bounty_rejection(b, to_emails)
        except Exception as e:
            logging.exception(e)

    return len(to_emails)


def maybe_post_on_craigslist(bounty):
    import time
    import mechanicalsoup
    from app.utils import fetch_last_email_id, fetch_mails_since_id

    craigslist_url = 'https://boulder.craigslist.org/'
    max_urls = 10

    browser = mechanicalsoup.StatefulBrowser()
    browser.open(craigslist_url)  # open craigslist
    post_link = browser.find_link(attrs={'id': 'post'})
    page = browser.follow_link(post_link)  # scraping the posting page link

    form = page.soup.form
    # select 'gig offered (I'm hiring for a short-term, small or odd job)'
    form.find('input', {'type': 'radio', 'value': 'go'})['checked'] = ''
    page = browser.submit(form, form['action'])

    form = page.soup.form
    # select 'I want to hire someone'
    form.find('input', {'type': 'radio', 'value': 'G'})['checked'] = ''
    page = browser.submit(form, form['action'])

    form = page.soup.form
    # select 'computer gigs (small web design, tech support, etc projects )'
    form.find('input', {'type': 'radio', 'value': '110'})['checked'] = ''
    page = browser.submit(form, form['action'])
    form = page.soup.form

    # keep selecting defaults for sub area etc till we reach edit page
    # this step is to ensure that we go over all the extra pages which appear on craigslist only in some locations
    # this choose the default skip options in craigslist
    for i in range(max_urls):
        if page.url.endswith('s=edit'):
            break
        # Chooses the first default
        if page.url.endswith('s=subarea'):
            form.find_all('input')[1]['checked'] = ''
        else:
            form.find_all('input')[0]['checked'] = ''
        page = browser.submit(form, form['action'])
        form = page.soup.form
    else:
        # for-else magic
        # if the loop completes normally that means we are still not at the edit page
        # hence return and don't proceed further
        print('returning at first return')
        return

    posting_title = bounty.title
    if not posting_title:
        posting_title = f"Please turn around {bounty.org_name}’s issue"
    posting_body = f"Solve this github issue: {bounty.github_url}"

    # Final form filling
    form.find('input', {'id': "PostingTitle"})['value'] = posting_title
    form.find('textarea', {'id': "PostingBody"}).insert(0, posting_body)
    form.find('input', {'id': "FromEMail"})['value'] = settings.IMAP_EMAIL
    form.find('input', {'id': "ConfirmEMail"})['value'] = settings.IMAP_EMAIL
    for postal_code_input in form.find_all('input', {'id': "postal_code"}):
        postal_code_input['value'] = '94105'
    form.find('input', {'value': 'pay', 'name': 'remuneration_type'})['checked'] = ''
    form.find('input', {'id': "remuneration"})['value'] = f"{bounty.get_natural_value()} {bounty.token_name}"
    try:
        form.find('input', {'id': "wantamap"})['data-checked'] = ''
    except Exception:
        pass
    page = browser.submit(form, form['action'])

    # skipping image upload
    form = page.soup.find_all('form')[-1]
    page = browser.submit(form, form['action'])

    for i in range(max_urls):
        if page.url.endswith('s=preview'):
            break
        # Chooses the first default
        page = browser.submit(form, form['action'])
        form = page.soup.form
    else:
        # for-else magic
        # if the loop completes normally that means we are still not at the edit page
        # hence return and don't proceed further
        print('returning at 2nd return')
        return

    # submitting final form
    form = page.soup.form
    # getting last email id
    last_email_id = fetch_last_email_id(settings.IMAP_EMAIL, settings.IMAP_PASSWORD)
    page = browser.submit(form, form['action'])
    time.sleep(10)
    last_email_id_new = fetch_last_email_id(settings.IMAP_EMAIL, settings.IMAP_PASSWORD)
    # if no email has arrived wait for 5 seconds
    if last_email_id == last_email_id_new:
        # could slow responses if called syncronously in a request
        time.sleep(5)

    emails = fetch_mails_since_id(settings.IMAP_EMAIL, settings.IMAP_PASSWORD, last_email_id)
    for _, content in emails.items():
        if 'craigslist' in content['from']:
            for link in re.findall(r"(?:https?:\/\/[a-zA-Z0-9%]+[.]+craigslist+[.]+org/[a-zA-Z0-9\/\-]*)", content.as_string()):
                # opening all links in the email
                try:
                    browser = mechanicalsoup.StatefulBrowser()
                    page = browser.open(link)
                    form = page.soup.form
                    page = browser.submit(form, form['action'])
                    return link
                except Exception:
                    # in case of invalid links
                    return False
    return False


def maybe_notify_bounty_user_escalated_to_slack(bounty, username, last_heard_from_user_days):
    if not settings.SLACK_TOKEN or bounty.get_natural_value() < 0.0001 or (
       bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
        return False

    msg = f"@vivek, {bounty.github_url} is being escalated to you, due to inactivity for {last_heard_from_user_days} days from @{username} on the github thread."

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channel = 'notif-gitcoin'
        sc.api_call("chat.postMessage", channel=channel, text=msg)
    except Exception as e:
        print(e)
        return False
    return True


# TODO: DRY with expiration_start_work
num_days_back_to_warn = 3
num_days_back_to_delete_interest = 6


def append_snooze_copy(bounty):
    """Build the snooze copy for the associated Bounty.

    Args:
        bounty (dashboard.Bounty): The Bounty to create snooze copy for.

    Returns:
        str: The snooze copy for the provided bounty.

    """
    snooze = []
    for day in [1, 3, 5, 10, 100]:
        plural = "s" if day != 1 else ""
        snooze.append(f"[{day} day{plural}]({bounty.snooze_url(day)})")
    snooze = " | ".join(snooze)
    return f"\nFunders only: Snooze warnings for {snooze}"


def maybe_notify_user_escalated_github(bounty, username, last_heard_from_user_days=None):
    if (not settings.GITHUB_CLIENT_ID) or (bounty.get_natural_value() < 0.0001) or (
       bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
        return False

    if not last_heard_from_user_days:
        last_heard_from_user_days = num_days_back_to_delete_interest

    status_header = get_status_header(bounty)

    msg = f"""{status_header}@{username} due to inactivity, we have escalated [this issue]({bounty.url}) to Gitcoin's moderation team. Let us know if you believe this has been done in error!

* [x] warning ({num_days_back_to_warn} days)
* [x] escalation to mods ({num_days_back_to_delete_interest} days)
{append_snooze_copy(bounty)}"""

    post_issue_comment(bounty.org_name, bounty.github_repo_name, bounty.github_issue_number, msg)


def maybe_warn_user_removed_github(bounty, username, last_heard_from_user_days):
    if (not settings.GITHUB_CLIENT_ID) or (bounty.get_natural_value() < 0.0001) or (
       bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
        return False

    msg = f"""@{username} Hello from Gitcoin Core - are you still working on this issue? Please submit a WIP PR or comment back within the next 3 days or you will be removed from this ticket and it will be returned to an ‘Open’ status. Please let us know if you have questions!
* [x] warning ({num_days_back_to_warn} days)
* [ ] escalation to mods ({num_days_back_to_delete_interest} days)
{append_snooze_copy(bounty)}"""

    post_issue_comment(bounty.org_name, bounty.github_repo_name, bounty.github_issue_number, msg)


def maybe_notify_bounty_user_warned_removed_to_slack(bounty, username, last_heard_from_user_days=None):
    if not settings.SLACK_TOKEN or bounty.get_natural_value() < 0.0001 or (
       bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
        return False

    msg = f"@{username} has been warned about inactivity ({last_heard_from_user_days} days) on {bounty.github_url}"

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channel = 'notif-gitcoin'
        sc.api_call("chat.postMessage", channel=channel, text=msg)
    except Exception as e:
        print(e)
        return False
    return True
