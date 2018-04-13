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
from django.utils import timezone

import rollbar
import twitter
from economy.utils import convert_token_to_usdt
from github.utils import delete_issue_comment, patch_issue_comment, post_issue_comment
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
        except:
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

    conv_details = ""
    usdt_details = ""
    try:
        conv_details = f"@ (${round(convert_token_to_usdt(bounty.token_name),2)}/{bounty.token_name})"
        usdt_details = f"({bounty.value_in_usdt_now} USD {conv_details} "
    except:
        pass #no USD conversion rate
    title = bounty.title if bounty.title else bounty.github_url
    msg = f"{event_name.replace('bounty', 'funded_issue')} worth {round(bounty.get_natural_value(), 4)} {bounty.token_name} " \
          f"{usdt_details}" \
          f"{bounty.token_name}: {title} \n\n{bounty.get_absolute_url()}"

    try:
        channel = 'notif-gitcoin'
        sc = SlackClient(settings.SLACK_TOKEN)
        sc.api_call("chat.postMessage", channel=channel, text=msg)
    except Exception as e:
        print(e)
        return False
    return True


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
        channel = 'bounties'
        sc.api_call("chat.postMessage", channel=channel, text=msg)
    except Exception as e:
        print(e)
        return False
    return True


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
    from dashboard.models import BountyFulfillment
    msg = ''
    usdt_value = ""
    try:
        usdt_value = f"({round(bounty.value_in_usdt_now, 2)} USD @ ${round(convert_token_to_usdt(bounty.token_name), 2)}/{bounty.token_name})" if bounty.value_in_usdt_now else ""
    except:
        pass # no USD conv rate available
    natural_value = round(bounty.get_natural_value(), 4)
    absolute_url = bounty.get_absolute_url()
    amount_open_work = amount_usdt_open_work()
    profiles = ""
    bounty_owner = f"(@{bounty.bounty_owner_github_username})" if bounty.bounty_owner_github_username else ""

    if profile_pairs:
        profiles = "\n 1. ".join("[@%s](%s)" % profile for profile in profile_pairs)
    if event_name == 'new_bounty':
        msg = f"__This issue now has a funding of {natural_value} " \
              f"{bounty.token_name} {usdt_value} attached to it.__\n\n * If you would " \
              f"like to work on this issue you can claim it [here]({absolute_url}).\n " \
              "* If you've completed this issue and want to claim the bounty you can do so " \
              f"[here]({absolute_url})\n * Questions? Get help on the " \
              f"<a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${amount_open_work}" \
              " more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
    if event_name == 'increased_bounty':
        msg = f"__The funding of this issue was increased to {natural_value} " \
              f"{bounty.token_name} {usdt_value}.__\n\n * If you would " \
              f"like to work on this issue you can claim it [here]({absolute_url}).\n " \
              "* If you've completed this issue and want to claim the bounty you can do so " \
              f"[here]({absolute_url})\n * Questions? Get help on the " \
              f"<a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${amount_open_work}" \
              " more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
    elif event_name == 'killed_bounty':
        msg = f"__The funding of {natural_value} {bounty.token_name} " \
              f"{usdt_value} attached to this issue has been **killed** by the bounty submitter__\n\n " \
              "* Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * " \
              f"${amount_open_work} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
    elif event_name == 'rejected_claim':
        msg = f"__The work submission for {natural_value} {bounty.token_name} {usdt_value} " \
              "has been **rejected** and can now be submitted by someone else.__\n\n * If you would " \
              f"like to work on this issue you can claim it [here]({absolute_url}).\n * If you've " \
              f"completed this issue and want to claim the bounty you can do so [here]({absolute_url})\n " \
              "* Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * " \
              f"${amount_open_work} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
    elif event_name == 'work_started':
        sub_msg = "\n\n __Please work together__ and coordinate delivery of the issue scope. Gitcoin " \
                  "doesn't know enough about everyones skillsets / free time to say who should work on " \
                  "what, but we trust that the community is smart and well-intentioned enough to work " \
                  "together.  As a general rule; if you start work first, youll be at the top of the " \
                  "above list ^^, and should have 'dibs' as long as you follow through. \n\n On the " \
                  f"above list? Please leave a comment to let the funder {bounty_owner} and the other parties " \
                  "involved what you're working, with respect to this issue and your plans to resolve " \
                  "it.  If you don't leave a comment, the funder may expire your submission at their discretion."

        msg = f"__Work has been started on the {natural_value} {bounty.token_name} {usdt_value} funding " \
              f"by__: \n 1. {profiles} {sub_msg} \n\n * Learn more [on the gitcoin issue page]({absolute_url})\n " \
              "* Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * " \
              f"${amount_open_work} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
    elif event_name == 'work_submitted':
        sub_msg = f"\n\n Submitters, please leave a comment to let the funder {bounty_owner} " \
                  "(and the other parties involved) that you've submitted you work.  If you don't " \
                  "leave a comment, the funder may expire your submission at their discretion."

        msg = f"__Work for {natural_value} {bounty.token_name} {usdt_value} has been submitted by__: \n 1. " \
              f"{profiles} {sub_msg} \n\n * Learn more [on the gitcoin issue page]({absolute_url})\n * " \
              "Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * " \
              f"${amount_open_work} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
    elif event_name == 'work_done':
        try:
            accepted_fulfillment = bounty.fulfillments.filter(accepted=True).latest('fulfillment_id')
            accepted_fulfiller = f' to @{accepted_fulfillment.fulfiller_github_username}'
        except BountyFulfillment.DoesNotExist:
            accepted_fulfiller = ''

        msg = f"__The funding of {natural_value} {bounty.token_name} {usdt_value} attached to this " \
              f"issue has been approved & issued{accepted_fulfiller}.__  \n\n * Learn more at [on the gitcoin " \
              f"issue page]({absolute_url})\n * Questions? Get help on the <a href='https://gitcoin.co/slack'>" \
              f"Gitcoin Slack</a>\n * ${amount_open_work} more Funded OSS Work Available at: " \
              "https://gitcoin.co/explorer\n"
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
    from marketing.mails import new_work_submission, new_bounty_rejection, new_bounty_acceptance, new_bounty
    from marketing.models import EmailSubscriber
    to_emails = []
    if b.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    if event_name == 'new_bounty' and not settings.DEBUG:
        try:
            # this doesnt scale because there are typically like 600 matches.. need to move to a background job
            return
            keywords = b.keywords.split(',')
            for keyword in keywords:
                to_emails = to_emails + list(EmailSubscriber.objects.filter(
                    keywords__contains=[keyword.strip()]).values_list('email', flat=True))

            should_send_email = b.web3_created > (timezone.now() - timezone.timedelta(hours=15))
            # only send if the bounty is reasonbly new

            if should_send_email:
                for to_email in set(to_emails):
                    new_bounty(b, [to_email])
        except Exception as e:
            logging.exception(e)
            print(e)
    elif event_name == 'work_submitted':
        try:
            to_emails = [b.bounty_owner_email]
            new_work_submission(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)
    elif event_name == 'work_done':
        accepted_fulfillment = b.fulfillments.filter(accepted=True).latest('modified_on')
        try:
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
