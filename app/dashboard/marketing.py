from django.conf import settings
import twitter
import requests
from urlparse import urlparse
from app.github import post_issue_comment


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
