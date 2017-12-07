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

import logging
from django.conf import settings
import twitter
import requests
from urllib import parse
from app.github import post_issue_comment
from slackclient import SlackClient
import re



def maybe_market_to_twitter(bounty, event_name, txid):

    if not settings.TWITTER_CONSUMER_KEY:
        return False
    if event_name != 'new_bounty':
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

    new_tweet = "New funded issue worth {} {} \n\n{}".format(
        round(bounty.get_natural_value(), 4),
        bounty.token_name,
        bounty.get_absolute_url()
    )
    if bounty.keywords:
        for keyword in bounty.keywords.split(','):
            _new_tweet = new_tweet + "#" + str(keyword).lower().strip()
            if len(_new_tweet) < 140:
                new_tweet = _new_tweet

    try:
        api.PostUpdate(new_tweet)
    except Exception as e:
        print(e)
        return False

    return True


def should_post_in_channel(channel, bounty):
    if channel in ['focus-bounties', 'focus-dev']:
        return True
    if 'focus-' in channel:
        keyword = channel.replace('focus-', '').replace('dev-', '').lower()
        return keyword in str(bounty.title).lower() \
            or keyword in str(bounty.keywords).lower() \
            or keyword in str(bounty.github_url).lower()

    return False


def maybe_market_to_slack(bounty, event_name, txid):
    if not settings.SLACK_TOKEN:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    title = bounty.title if bounty.title else bounty.github_url
    msg = "{} worth {} {}: {} \n\n{}&slack=1".format(event_name.replace('bounty', 'funded_issue'), round(bounty.get_natural_value(), 4), bounty.token_name, title, bounty.get_absolute_url())

    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        channels = sc.api_call("channels.list")
        channels = [chan['name'] for chan in channels['channels']]
        channels_to_post_in = [channel for channel in channels if should_post_in_channel(channel, bounty)]
        for channel in channels_to_post_in:
            sc.api_call(
              "chat.postMessage",
              channel=channel,
              text=msg,
            )
    except Exception as e:
        print(e)
        return False

    return True


def maybe_market_tip_to_slack(tip, event_name, txid):
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


def maybe_market_to_github(bounty, event_name, txid):
    if not settings.GITHUB_CLIENT_ID:
        return False
    if bounty.get_natural_value() < 0.0001:
        return False
    if bounty.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    # prepare message
    msg = ''
    if event_name == 'new_bounty':
        usdt_value = "(" + str(round(bounty.value_in_usdt, 2)) + " USD)" if bounty.value_in_usdt else ""
        msg = "__This issue now has a funding of {} {} {} attached to it.__\n\n * If you would like to work on this issue you can claim it [here]({}).\n * If you've completed this issue and want to claim the bounty you can do so [here]({})\n".format(round(bounty.get_natural_value(), 4), bounty.token_name, usdt_value, bounty.get_absolute_url(), bounty.get_absolute_url())
    elif event_name == 'approved_claim':
        msg = "__The funding of {} {} attached to this issue has been approved & issued.__  \n\nLearn more at: {}".format(round(bounty.get_natural_value(), 4), bounty.token_name, bounty.get_absolute_url())
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
    if tip.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
        return False

    # prepare message
    username = tip.username if '@' in tip.username else str('@' + tip.username)
    _from = " from {}".format(tip.from_name) if tip.from_name else ""
    warning = tip.network if tip.network != 'mainnet' else ""
    msg = "⚡️ A tip worth {} {} {} has been granted to {} for this issue{}. ⚡️ \n\nNice work {}, check your email for further instructions. | <a href='https://gitcoin.co/tip'>Send a Tip</a>".format(round(tip.amount, 3), warning, tip.tokenName, username, _from, username)

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


def maybe_market_to_email(b, event_name, txid):
    from marketing.mails import new_bounty_claim, new_bounty_rejection, new_bounty_acceptance, new_bounty
    from marketing.models import EmailSubscriber
    to_emails = []

    if event_name == 'new_bounty':
        try:
            to_emails = []
            keywords = b.keywords.split(',')
            for keyword in keywords:
                to_emails = to_emails + list(EmailSubscriber.objects.filter(keywords__contains=[keyword.strip()]).values_list('email', flat=True))
            for to_email in set(to_emails):
                new_bounty(b, [to_email])
        except Exception as e:
            logging.exception(e)
            print(e)
    if event_name == 'new_claim':
        try:
            to_emails = [b.bounty_owner_email]
            new_bounty_claim(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)
    if event_name == 'approved_claim':
        try:
            to_emails = [b.bounty_owner_email, b.claimee_email]
            new_bounty_acceptance(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)
    if event_name == 'rejected_claim':
        try:
            to_emails = [b.bounty_owner_email, b.claimee_email]
            new_bounty_rejection(b, to_emails)
        except Exception as e:
            logging.exception(e)
            print(e)

    return len(to_emails)

def maybe_post_on_craigslist(bounty):
    CRAIGSLIST_URL = 'https://boulder.craigslist.org/'
    MAX_URLS = 10

    import mechanicalsoup
    from random import randint
    from app.utils import fetch_last_email_id,fetch_mails_since_id
    import time

    browser = mechanicalsoup.StatefulBrowser()
    browser.open(CRAIGSLIST_URL) # open craigslist
    post_link = browser.find_link(attrs={'id': 'post'})
    page = browser.follow_link(post_link) # scraping the posting page link

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
        #Chooses the first default
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
    except:
        pass
    page = browser.submit(form, form['action'])

    # skipping image upload
    form = page.soup.find_all('form')[-1]
    page = browser.submit(form, form['action'])

    for i in range(MAX_URLS):
        if page.url.endswith('s=preview'):
            break
        #Chooses the first default
        page = browser.submit(form, form['action'])
        form = page.soup.form
    else:
        # for-else magic
        # if the loop completes normally that means we are still not at the edit page
        # hence return and don't proceed further
        return


    # submitting final form
    form = page.soup.form 
    #getting last email id
    last_email_id = fetch_last_email_id(settings.IMAP_EMAIL, settings.IMAP_PASSWORD)
    page = browser.submit(form, form['action'])
    time.sleep(10)
    last_email_id_new = fetch_last_email_id(settings.IMAP_EMAIL, settings.IMAP_PASSWORD)
    #if no email has arrived wait for 5 seconds
    if last_email_id==last_email_id_new:
        # could slow responses if called syncronously in a request
        time.sleep(5)

    emails = fetch_mails_since_id( settings.IMAP_EMAIL, settings.IMAP_PASSWORD,last_email_id)
    for email_id, content in emails.items():
        if 'craigslist' in content['from']:
            for link in re.findall(r"(?:https?:\/\/[a-zA-Z0-9%]+[.]+craigslist+[.]+org/[a-zA-Z0-9\/\-]*)", content.as_string()):
                # opening all links in the email
                try:
                    browser = mechanicalsoup.StatefulBrowser()
                    page = browser.open(link)
                    form = page.soup.form 
                    page = browser.submit(form, form['action'])
                    return link
                except:
                    # in case of inavalid links
                    False
            else:
                return False
