import logging
import random
import re
import sys
from urllib.parse import urlparse as parse

from django.conf import settings

import rollbar
import twitter
from github.utils import delete_issue_comment, patch_issue_comment, post_issue_comment
from marketing.mails import tip_email
from marketing.models import GithubOrgToTwitterHandleMapping
from pyshorteners import Shortener
from slackclient import SlackClient


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


def github_org_to_twitter_tags(github_org):
    twitter_handles = GithubOrgToTwitterHandleMapping.objects.filter(github_orgname__iexact=github_org)
    twitter_handles = twitter_handles.values_list('twitter_handle', flat=True)
    twitter_tags = " ".join(["@{}".format(ele) for ele in twitter_handles])
    return twitter_tags


def maybe_market_to_twitter(bounty, event_name):
    """Tweet the specified Bounty event."""
    if not settings.TWITTER_CONSUMER_KEY:
        return False
    if event_name not in ['new_bounty', 'remarket_bounty']:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False
    return False # per 2018/01/22 convo with vivek / kevin, these tweets have low engagement
    # we are going to test manually promoting these tweets for a week and come back to revisit this

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
    if event_name == 'new_bounty':
        tweet_txts = tweet_txts + [
            "Extra! Extra 🗞🗞 New Funded Issue, Read all about it 👇  {} {} {} \n\n{}",
            "Hot off the blockchain! 🔥🔥🔥 There's a new task worth {} {} {} \n\n{}",
            "💰 New Task Alert.. 💰 Earn {} {} {} for working on this 👇 \n\n{}",
        ]

    random.shuffle(tweet_txts)
    tweet_txt = tweet_txts[0]

    shortener = Shortener('Tinyurl')

    new_tweet = tweet_txt.format(
        round(bounty.get_natural_value(), 4),
        bounty.token_name,
        ("(${})".format(bounty.value_in_usdt) if bounty.value_in_usdt else ""),
        shortener.short(bounty.get_absolute_url())
    )
    new_tweet = new_tweet + " " + github_org_to_twitter_tags(bounty.org_name) #twitter tags
    if bounty.keywords: #hashtags
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

    title = bounty.title if bounty.title else bounty.github_url
    msg = "{} worth {} {}: {} \n\n{}&slack=1".format(event_name.replace('bounty', 'funded_issue'), round(bounty.get_natural_value(), 4), bounty.token_name, title, bounty.get_absolute_url())

    try:
        channel = 'notif-gitcoin'
        sc = SlackClient(settings.SLACK_TOKEN)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
        )
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
    if not settings.SLACK_TOKEN:
        return False
    if tip.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
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


def maybe_market_to_github(bounty, event_name, interested=None):
    """Post a Github comment for the specified Bounty.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to be marketed.
        event_name (str): The name of the event.
        interested (list of tuples): The list of username and profile page URL
            tuple pairs.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    if not settings.GITHUB_CLIENT_ID:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    # prepare message
    msg = ''
    usdt_value = "(" + str(round(bounty.value_in_usdt, 2)) + " USD)" if bounty.value_in_usdt else ""
    if event_name == 'new_bounty':
        msg = "__This issue now has a funding of {} {} {} attached to it.__\n\n * If you would like to work on this issue you can claim it [here]({}).\n * If you've completed this issue and want to claim the bounty you can do so [here]({})\n * Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
        msg = msg.format(
            round(bounty.get_natural_value(), 4),
            bounty.token_name, usdt_value,
            bounty.get_absolute_url(),
            bounty.get_absolute_url(),
            amount_usdt_open_work(),
            )
    elif event_name == 'killed_bounty':
        msg = "__The funding of {} {} {} attached to this issue has been **killed** by the bounty submitter__\n\n * Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
        msg = msg.format(
            round(bounty.get_natural_value(), 4),
            bounty.token_name, usdt_value,
            amount_usdt_open_work(),
            )
    elif event_name == 'rejected_claim':
        msg = "__The work submission for {} {} {} has been **rejected** and can now be submitted by someone else.__\n\n * If you would like to work on this issue you can claim it [here]({}).\n * If you've completed this issue and want to claim the bounty you can do so [here]({})\n * Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
        msg = msg.format(
            round(bounty.get_natural_value(), 4),
            bounty.token_name, usdt_value,
            bounty.get_absolute_url(),
            bounty.get_absolute_url(),
            amount_usdt_open_work(),
            )
    elif event_name == 'work_started':
        msg = "__Work has been started on the {} {} {} funding by: {}.__ {} \n\n * Learn more [on the gitcoin issue page]({})\n * Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
        # Build interested profiles string.
        interested_profiles = ", ".join("[@%s](%s)" % interest for interest in interested)
        msg = msg.format(
            round(bounty.get_natural_value(), 4),
            bounty.token_name,
            usdt_value,
            interested_profiles if interested_profiles else "",
            "\n\n If you've started work, please leave a comment to let the funder {} and the other parties involved what you're working, with respect to this issue and your plans to resolve it.  If you don't leave a comment, the funder may expire your submission at their discretion.".format(
                "(@{})".format(bounty.bounty_owner_github_username) if bounty.bounty_owner_github_username else "",
                ),
            bounty.get_absolute_url(),
            amount_usdt_open_work(),
        )
    elif event_name == 'work_submitted':
        msg = "__Work for {} {} {} has been submitted {}.__ {} \n\n * Learn more [on the gitcoin issue page]({})\n * Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
        msg = msg.format(
            round(bounty.get_natural_value(), 4),
            bounty.token_name,
            usdt_value,
            "by @{}".format(bounty.fulfiller_github_username) if bounty.fulfiller_github_username else "",
            "\n\n {}, please leave a comment to let the funder {} (and the other parties involved) that you've submitted you work.  If you don't leave a comment, the funder may expire your submission at their discretion.".format(
                "@{}".format(bounty.fulfiller_github_username) if bounty.fulfiller_github_username else "If you are the claimee",
                "(@{})".format(bounty.bounty_owner_github_username) if bounty.bounty_owner_github_username else "",
                ),
            bounty.get_absolute_url(),
            amount_usdt_open_work(),
            )
    elif event_name == 'work_done':
        msg = "__The funding of {} {} {} attached to this issue has been approved & issued {}.__  \n\n * Learn more at [on the gitcoin issue page]({})\n * Questions? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>\n * ${} more Funded OSS Work Available at: https://gitcoin.co/explorer\n"
        msg = msg.format(
            round(bounty.get_natural_value(), 4),
            bounty.token_name,
            usdt_value,
            "to @{}".format(bounty.fulfiller_github_username) if bounty.fulfiller_github_username else "",
            bounty.get_absolute_url(),
            amount_usdt_open_work(),
            )
    else:
        return False

    # actually post
    url = bounty.github_url
    uri = parse(url).path
    uri_array = uri.split('/')
    try:
        username = uri_array[1]
        repo = uri_array[2]
        issue_num = uri_array[4]

        if event_name == 'work_started' and interested:
            if bounty.interested_comment is not None:
                patch_issue_comment(bounty.interested_comment, username, repo, msg)
            else:
                response = post_issue_comment(username, repo, issue_num, msg)
                if response.get('id'):
                    bounty.interested_comment = int(response.get('id'))
                    bounty.save()
        elif event_name == 'work_started' and not interested:
            delete_issue_comment(bounty.interested_comment, username, repo)
            bounty.interested_comment = None
            bounty.save()
        else:
            post_issue_comment(username, repo, issue_num, msg)

    except Exception as e:
        extra_data = {'github_url': url, 'bounty_id': bounty.pk, 'event_name': event_name}
        rollbar.report_exc_info(sys.exc_info(), extra_data=extra_data)
        print(e)
        return False

    return True


def amount_usdt_open_work():
    from dashboard.models import Bounty
    bounties = Bounty.objects.filter(network='mainnet', current_bounty=True, idx_status__in=['open', 'submitted'])
    return round(sum([b.value_in_usdt for b in bounties]), 2)


def maybe_market_tip_to_github(tip):
    """Post a Github comment for the specified Tip.

    Args:
        tip (dashboard.models.Tip): The Tip to be marketed.

    Returns:
        bool: Whether or not the Github comment was posted successfully.

    """
    if not settings.GITHUB_CLIENT_ID:
        return False
    if not tip.github_url:
        return False
    if tip.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    # prepare message
    username = tip.username if '@' in tip.username else str('@' + tip.username)
    _from = " from {}".format(tip.from_name) if tip.from_name else ""
    warning = tip.network if tip.network != 'mainnet' else ""
    _comments = "\n\nThe sender had the following public comments: \n> {}".format(tip.comments_public) if tip.comments_public else ""
    msg = "⚡️ A tip worth {} {} {} {} has been granted to {} for this issue{}. ⚡️ {}\n\nNice work {}, check your email for further instructions. \n\n * ${} in Funded OSS Work Available at: https://gitcoin.co/explorer\n * Incentivize contributions to your repo: <a href='https://gitcoin.co/tip'>Send a Tip</a> or <a href='https://gitcoin.co/funding/new'>Fund a PR</a>\n * No Email? Get help on the <a href='https://gitcoin.co/slack'>Gitcoin Slack</a>"
    msg = msg.format(round(tip.amount, 5), warning, tip.tokenName, "(${})".format(tip.value_in_usdt) if tip.value_in_usdt else "" , username, _from, _comments, username, amount_usdt_open_work())

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
            keywords = b.keywords.split(',')
            for keyword in keywords:
                to_emails = to_emails + list(EmailSubscriber.objects.filter(keywords__contains=[keyword.strip()]).values_list('email', flat=True))
            for to_email in set(to_emails):
                new_bounty(b, [to_email])
        except Exception as e:
            logging.exception(e)
            print(e)
    if event_name == 'work_submitted':
        try:
            to_emails = [b.bounty_owner_email]
            new_work_submission(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)
    if event_name == 'work_done':
        try:
            to_emails = [b.bounty_owner_email, b.fulfiller_email]
            new_bounty_acceptance(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)
    if event_name == 'rejected_claim':
        try:
            to_emails = [b.bounty_owner_email, b.fulfiller_email]
            new_bounty_rejection(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)

    return len(to_emails)


def maybe_post_on_craigslist(bounty):
    CRAIGSLIST_URL = 'https://boulder.craigslist.org/'
    MAX_URLS = 10

    import mechanicalsoup
    from app.utils import fetch_last_email_id, fetch_mails_since_id
    import time

    browser = mechanicalsoup.StatefulBrowser()
    browser.open(CRAIGSLIST_URL)  # open craigslist
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
    for i in range(MAX_URLS):
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
        return

    posting_title = bounty.title
    if posting_title is None or posting_title == "":
        posting_title = "Please turn around {}’s issue".format(bounty.org_name)
    posting_body = "Solve this github issue: {}".format(bounty.github_url)

    # Final form filling
    form.find('input', {'id': "PostingTitle"})['value'] = posting_title
    form.find('textarea', {'id': "PostingBody"}).insert(0, posting_body)
    form.find('input', {'id': "FromEMail"})['value'] = settings.IMAP_EMAIL
    form.find('input', {'id': "ConfirmEMail"})['value'] = settings.IMAP_EMAIL
    for postal_code_input in form.find_all('input', {'id': "postal_code"}):
        postal_code_input['value'] = '94105'
    form.find('input', {'value': 'pay', 'name': 'remuneration_type'})['checked'] = ''
    form.find('input', {'id': "remuneration"})['value'] = "{} {}".format(bounty.get_natural_value(), bounty.token_name)
    try:
        form.find('input', {'id': "wantamap"})['data-checked'] = ''
    except Exception:
        pass
    page = browser.submit(form, form['action'])

    # skipping image upload
    form = page.soup.find_all('form')[-1]
    page = browser.submit(form, form['action'])

    for i in range(MAX_URLS):
        if page.url.endswith('s=preview'):
            break
        # Chooses the first default
        page = browser.submit(form, form['action'])
        form = page.soup.form
    else:
        # for-else magic
        # if the loop completes normally that means we are still not at the edit page
        # hence return and don't proceed further
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
            else:
                return False
