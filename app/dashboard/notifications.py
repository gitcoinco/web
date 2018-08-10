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

import requests
import rollbar
import twitter
from django.template.loader import render_to_string
from economy.utils import convert_token_to_usdt
from github.utils import delete_issue_comment, org_name, patch_issue_comment, post_issue_comment, repo_name
from types import SimpleNamespace
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
    if not bounty.is_notification_eligible(var_to_check=settings.TWITTER_CONSUMER_KEY):
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
    elif event_name == 'increased_bounty':
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
    elif event_name == 'worker_rejected':
        tweet_txts = [
            'Worked rejected on {} {} {}\n{}'
        ]
    elif event_name == 'worker_approved':
        tweet_txts = [
            'Worked approved on {} {} {}\n{}'
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
    if not bounty.is_notification_eligible(var_to_check=settings.SLACK_TOKEN):
        return False

    msg = build_message_for_integration(bounty, event_name)
    if not msg:
        return False

    try:
        channel = 'notif-gitcoin'
        sc = SlackClient(settings.SLACK_TOKEN)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            icon_url=settings.GITCOIN_SLACK_ICON_URL,
        )
    except Exception as e:
        print(e)
        return False
    return True


def build_message_for_integration(bounty, event_name):
    """Build message to be posted to integrated service (e.g. slack, discord).

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.

    Returns:
        str: Message to post to slack.

    """
    from dashboard.utils import humanize
    conv_details = ""
    usdt_details = ""
    try:
        conv_details = f"@ (${round(convert_token_to_usdt(bounty.token_name),2)}/{bounty.token_name})"
        usdt_details = f"({bounty.value_in_usdt_now} USD {conv_details} "
    except Exception:
        pass  # no USD conversion rate

    title = bounty.title if bounty.title else bounty.github_url
    msg = f"*{humanize(event_name.replace('bounty', 'funded_issue'))}*" \
          f"\n*Title*: {title}" \
          f"\n*Bounty value*: {round(bounty.get_natural_value(), 4)} {bounty.token_name} {usdt_details}" \
          f"\n{bounty.get_absolute_url()}"
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

    msg = build_message_for_integration(bounty, event_name)
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
                sc.api_call(
                    "chat.postMessage",
                    channel=subscriber.slack_channel,
                    text=msg,
                    icon_url=settings.GITCOIN_SLACK_ICON_URL,
                )
                sent = True
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

    return sent


def maybe_market_to_user_discord(bounty, event_name):
    """Send a Discord message to the user's discord channel for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.

    Returns:
        bool: Whether or not the Discord notification was sent successfully.

    """
    from dashboard.models import Profile
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    msg = build_message_for_integration(bounty, event_name)
    if not msg:
        return False

    url = bounty.github_url
    sent = False
    try:
        repo = org_name(url) + '/' + repo_name(url)
        subscribers = Profile.objects.filter(discord_repos__contains=[repo])
        subscribers = subscribers & Profile.objects.exclude(discord_webhook_url='')
        for subscriber in subscribers:
            try:
                headers = {'Content-Type': 'application/json'}
                body = {"content": msg, "avatar_url": "https://gitcoin.co/static/v2/images/helmet.png"}
                discord_response = requests.post(
                    subscriber.discord_webhook_url, headers=headers, json=body
                )
                if discord_response.status_code == 204:
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
    if not tip.is_notification_eligible(var_to_check=settings.SLACK_TOKEN):
        return False

    title = tip.github_url
    msg = f"{event_name} worth {round(tip.amount, 4)} {tip.tokenName}: {title} \n\n{tip.github_url}"

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channel = 'notif-gitcoin'
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            icon_url=settings.GITCOIN_SLACK_ICON_URL,
        )
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


def build_related_profile_pairs(queryset_all):
    # *args:
    #   a 1: bool: .filter(pending=True}False)
    queryset_all = queryset_all.select_related('profile').only('profile__handle')
    return queryset_all


def create_github_notifications():
    from dashboard.models import BountyFulfillment, Interest
    TEMPLATE_PATH = 'github_comments/'

    def new_bounty(context):
        context['amount_open_work'] = amount_usdt_open_work()
        msg = render_to_string(TEMPLATE_PATH + 'issue_opened.md', context)
        return msg

    def killed_bounty(context):
        bounty = context['bounty']
        if bounty.opened_comment:
            msg = bounty.opened_comment
        return msg

    def work_started(context):
        bounty = context['bounty']
        interested = bounty.interested.all().order_by('created')
        bounty_owner_clear = f"@{bounty.bounty_owner_github_username}" if bounty.bounty_owner_github_username else ""
        msg = {}
        if bounty.permission_type == 'approval' and interested:
            pending_interest = interested.filter(pending=True).only('issue_message', 'profile')
            interested_context = []
            for interest in pending_interest:
                interested_context.append(
                    SimpleNamespace(
                        profile=interest.profile,
                        approve_link=bounty.approve_worker_url(interest.profile.handle),
                        reject_link=bounty.reject_worker_url(interest.profile.handle),
                        issue_message=interest.issue_message
                    )
                )
            context['interested'] = interested_context
            msg['pending'] = render_to_string(TEMPLATE_PATH + 'express_interest.md', context)
            return msg
        started_work = build_related_profile_pairs(interested.filter(pending=False))
        if started_work:
            context['started_work'] = started_work
            msg['started'] = render_to_string(TEMPLATE_PATH + 'start_work.md', context)
        return msg

    def stop_work(context):
        bounty = context['bounty']
        interested = bounty.interested.all().order_by('created')
        still_working = build_related_profile_pairs(interested.filter(pending=False))
        still_working_handles = [interest.profile.handle for interest in still_working]

        context['still_working'] = [interest.profile for interest in still_working]
        context['stopped_work'] = [activity.profile for activity in build_related_profile_pairs(bounty.activities.filter(activity_type='stop_work')) if activity.profile.handle not in still_working_handles]

        msg = render_to_string(TEMPLATE_PATH + 'stop_work.md', context)
        return msg

    def work_submitted(context):
        bounty = context['bounty']
        context['fulfillments'] = [fulfillment.profile for fulfillment in build_related_profile_pairs(bounty.fulfillments.all())]
        msg = render_to_string(TEMPLATE_PATH + 'submit_work.md', context)
        return msg

    def work_done(context):
        bounty = context['bounty']
        try:
            context['accepted_fulfillment'] = bounty.fulfillments.filter(accepted=True).latest('fulfillment_id')
        except BountyFulfillment.DoesNotExist:
            context['accepted_fulfillment'] = None

        if bounty.done_comment and bounty.fulfillments.filter(accepted=True).count() == 0:
            msg = bounty.done_comment

        msg = render_to_string(TEMPLATE_PATH + 'accept_work.md', context)
        return msg

    events = {}

    events['new_bounty'] = new_bounty
    events['killed_bounty'] = killed_bounty
    events['increased_bounty'] = new_bounty
    events['work_started'] = work_started
    events['stop_work'] = stop_work
    events['work_submitted'] = work_submitted
    events['work_done'] = work_done

    return events

def build_github_notification(market_to_github):
    """Build a Github comment for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.
        profile_pairs (list of tuples): The list of username and profile page
            URL tuple pairs.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    def build_github_notification_market_to_github(*args, **kwargs):
        events = create_github_notifications()
        context = {
                        'bounty': args[0]
                  }
        msg = events[args[1]](context)
        return market_to_github(args[0], msg, args[1])
    return build_github_notification_market_to_github


@build_github_notification
def maybe_market_to_github(bounty, msg, event_name):
    """Post a Github comment for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.
        profile_pairs (list of tuples): The list of username and profile page
            URL tuple pairs.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    if msg is False or not bounty.is_notification_eligible(var_to_check=settings.GITHUB_CLIENT_ID):
        return False

    # Define posting specific variables.
    comment_id = None
    url = bounty.github_url
    uri = parse(url).path
    uri_array = uri.split('/')

    # Prepare the comment message string.
    if msg == bounty.done_comment or msg == bounty.opened_comment:
            delete_issue_comment(msg, username, repo)

    # Try either posting or patching the comment on the github issue
    try:
        username = uri_array[1]
        repo = uri_array[2]
        issue_num = uri_array[4]

        if event_name in ['new_bounty', 'increased_bounty']:
            if bounty.opened_comment:
                patch_issue_comment(bounty.opened_comment, username, repo, msg)
            else:
                response = post_issue_comment(username, repo, issue_num, msg)
                bounty.opened_comment = int(response.get('id'))
        elif event_name == 'work_started':
            if bounty.interested.filter(pending=True).count():
                if bounty.interested_comment:
                    patch_issue_comment(bounty.interested_comment, username, repo, msg['pending'])
                else:
                    response = post_issue_comment(username, repo, issue_num, msg['pending'])
                    bounty.interested_comment = int(response.get('id'))
            if bounty.interested.filter(pending=False).count():
                if bounty.started_comment:
                    patch_issue_comment(bounty.started_comment, username, repo, msg['started'])
                else:
                    response = post_issue_comment(username, repo, issue_num, msg['started'])
                    bounty.started_comment = int(response.get('id'))
        elif event_name == 'stop_work':
            if bounty.stopped_comment:
                patch_issue_comment(bounty.stopped_comment, username, repo, msg)
            else:
                response = post_issue_comment(username, repo, issue_num, msg)
                bounty.stopped_comment = int(response.get('id'))
        elif event_name == 'work_submitted':
            if bounty.submissions_comment:
                patch_issue_comment(bounty.submissions_comment, username, repo, msg)
            else:
                response = post_issue_comment(username, repo, issue_num, msg)
                bounty.submissions_comment = int(response.get('id'))
        elif event_name == 'work_done':
            if bounty.done_comment:
                patch_issue_comment(bounty.done_comment, username, repo, msg)
            else:
                response = post_issue_comment(username, repo, issue_num, msg)
                bounty.done_comment = int(response.get('id'))
        bounty.save()
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
    bounties = open_bounties()
    return round(sum([b.value_in_usdt_now for b in bounties if b.value_in_usdt_now]), 2)


def open_bounties():
    """Get all current open and submitted work.

    Returns:
        QuerySet: The mainnet Bounty objects which are of open and submitted work statuses.

    """
    from dashboard.models import Bounty, Profile
    return Bounty.objects.filter(network=Profile.get_network(), current_bounty=True, idx_status__in=['open', 'submitted'])

def maybe_market_tip_to_github(tip):
    """Post a Github comment for the specified Tip.

    Args:
        tip (dashboard.models.Tip): The Tip to be marketed.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    if not tip.is_notification_eligible(var_to_check=settings.GITHUB_CLIENT_ID) or not tip.github_url:
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
    if not bounty.is_notification_eligible(var_to_check=settings.SLACK_TOKEN):
        return False

    msg = f"<@U88M8173P>, {bounty.github_url} is being escalated to you, due to inactivity for {last_heard_from_user_days} days from <@{username}> on the github thread."

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channel = 'notif-gitcoin'
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            icon_url=settings.GITCOIN_SLACK_ICON_URL,
        )
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
    if not bounty.is_notification_eligible(var_to_check=settings.GITHUB_CLIENT_ID):
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
    if not bounty.is_notification_eligible(var_to_check=settings.GITHUB_CLIENT_ID):
        return False

    msg = f"""@{username} Hello from Gitcoin Core - are you still working on this issue? Please submit a WIP PR or comment back within the next 3 days or you will be removed from this ticket and it will be returned to an ‘Open’ status. Please let us know if you have questions!
* [x] warning ({num_days_back_to_warn} days)
* [ ] escalation to mods ({num_days_back_to_delete_interest} days)
{append_snooze_copy(bounty)}"""

    post_issue_comment(bounty.org_name, bounty.github_repo_name, bounty.github_issue_number, msg)


def maybe_notify_bounty_user_warned_removed_to_slack(bounty, username, last_heard_from_user_days=None):
    if not bounty.is_notification_eligible(var_to_check=settings.SLACK_TOKEN):
        return False

    msg = f"*@{username}* has been warned about inactivity ({last_heard_from_user_days} days) on {bounty.github_url}"

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channel = 'notif-gitcoin'
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            icon_url=settings.GITCOIN_SLACK_ICON_URL,
        )
    except Exception as e:
        print(e)
        return False
    return True
