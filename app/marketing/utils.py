# -*- coding: utf-8 -*-
'''
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

'''
import logging
import sys
from datetime import datetime, timedelta

from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

import requests
from mailchimp3 import MailChimp
from marketing.models import AccountDeletionRequest, LeaderboardRank
from slackclient import SlackClient
from slackclient.exceptions import SlackClientError

logger = logging.getLogger(__name__)


def delete_user_from_mailchimp(email_address):
    client = MailChimp(mc_user=settings.MAILCHIMP_USER, mc_api=settings.MAILCHIMP_API_KEY)
    result = None
    try:
        result = client.search_members.get(query=email_address)
        if result:
            subscriber_hash = result.get('exact_matches', {}).get('members', [{}])[0].get('id', None)
    except Exception as e:
        logger.debug(e)


        try:
            client.lists.members.delete(
                list_id=settings.MAILCHIMP_LIST_ID,
                subscriber_hash=subscriber_hash,
            )
        except Exception as e:
            logger.debug(e)

        try:
            client.lists.members.delete(
                list_id=settings.MAILCHIMP_LIST_ID_HUNTERS,
                subscriber_hash=subscriber_hash,
            )
        except Exception as e:
            logger.debug(e)

        try:
            client.lists.members.delete(
                list_id=settings.MAILCHIMP_LIST_ID_HUNTERS,
                subscriber_hash=subscriber_hash,
            )
        except Exception as e:
            logger.debug(e)


def is_deleted_account(handle):
    return AccountDeletionRequest.objects.filter(handle__iexact=handle).exists()


def get_stat(key):
    from marketing.models import Stat
    return Stat.objects.filter(key=key).order_by('-created_on').first().val


def invite_to_slack(email):
    if settings.DEBUG:
        return {}
    sc = SlackClient(settings.SLACK_TOKEN)
    response = sc.api_call('users.admin.invite', email=email)
    return response


def validate_slack_integration(token, channel, message=None, icon_url=''):
    """Validate the Slack token and channel combination by posting a message.

    Args:
        token (str): The Slack API token.
        channel (str): The Slack channel to send the message.
        message (str): The Slack message to be sent.
            Defaults to: The Gitcoin Slack integration is working fine.
        icon_url (str): The URL to the avatar to be used.
            Defaults to: the gitcoin helmet.

    Attributes:
        result (dict): The result dictionary defining success status and error message.
        error_messages (dict): The dictionary mapping of expected error result types.
        message (str): The response message to display to the user.
        sc (SlackClient): The slack client object.
        response (dict): The Slack response payload.
        error (str): The error code

    Raises:
        SlackClientError: The exception is raised for any Slack-specific error.

    Returns:
        str: The response message.

    """
    result = {'success': False, 'output': ''}
    error_messages = {
        'invalid_auth': _('Invalid Slack token.'),
        'channel_not_found': _('Slack channel not found.'),
    }

    if message is None:
        message = gettext('The Gitcoin Slack integration is working fine.')

    if not icon_url:
        icon_url = static('v2/images/helmet.png')

    try:
        sc = SlackClient(token)
        response = sc.api_call(
            'chat.postMessage',
            channel=channel,
            text=message,
            icon_url=icon_url)
        error = response.get('error', '')

        if error:
            result['output'] = error_messages.get(error, error.replace('_', ' ').title())
        elif 'ok' in response:
            result['output'] = _('The test message was sent to Slack.')
            result['success'] = True
    except SlackClientError as e:
        logger.error(e)
        result['output'] = _('An error has occurred.')
    return result


def validate_discord_integration(webhook_url, message=None, icon_url=''):
    """Validate the Discord webhook URL by posting a message.

    Args:
        webhook_url (str): The Discord webhook URL.
        message (str): The Discord message to be sent.
            Defaults to: The Gitcoin Discord integration is working fine.
        icon_url (str): The URL to the avatar to be used.
            Defaults to: the gitcoin helmet.

    Attributes:
        result (dict): The result dictionary defining success status and error message.
        message (str): The response message to display to the user.
        response (obj): The Discord response object - refer to python-requests API

    Raises:
        requests.exception.HTTPError: The exception is raised for any HTTP error.

    Returns:
        str: The response message.

    """
    result = {'success': False, 'output': 'Test message was not sent.'}

    if message is None:
        message = gettext('The Gitcoin Discord integration is working fine.')

    if not icon_url:
        icon_url = static('v2/images/helmet.png')

    try:
        headers = {'Content-Type': 'application/json'}
        body = {"content": message, "avatar_url": icon_url}
        response = requests.post(
            webhook_url, headers=headers, json=body
        )
        response.raise_for_status()
        if response.ok:
            result['output'] = _('The test message was sent to Discord.')
            result['success'] = True
    except requests.exceptions.HTTPError as e:
        logger.error(e)
        result['output'] = _('An error has occurred.')
    return result


def should_suppress_notification_email(email, email_type):
    from marketing.models import EmailSubscriber
    queryset = EmailSubscriber.objects.filter(email__iexact=email)
    if queryset.exists():
        es = queryset.first()
        return not es.should_send_email_type_to(email_type)
    return False


def get_or_save_email_subscriber(email, source, send_slack_invite=True, profile=None):
    from marketing.models import EmailSubscriber
    defaults = {'source': source, 'email': email}

    if profile:
        defaults['profile'] = profile

    try:
        es, created = EmailSubscriber.objects.update_or_create(email__iexact=email, defaults=defaults)
        print("EmailSubscriber:", es, "- created" if created else "- updated")
    except EmailSubscriber.MultipleObjectsReturned:
        email_subscriber_ids = EmailSubscriber.objects.filter(email__iexact=email) \
            .values_list('id', flat=True) \
            .order_by('-created_on')[1:]
        EmailSubscriber.objects.filter(pk__in=list(email_subscriber_ids)).delete()
        es = EmailSubscriber.objects.get(email__iexact=email)
        created = False
    except EmailSubscriber.DoesNotExist:
        es = EmailSubscriber.objects.create(**defaults)
        created = True
    except Exception as e:
        print(f'Failed to update or create email subscriber: ({email}) - {e}')
        return ''

    if created or not es.priv:
        es.set_priv()
        es.save()
        if send_slack_invite:
            invite_to_slack(email)

    return es


def get_platform_wide_stats(since_last_n_days=90):
    """Get platform wide stats for quarterly stats email.

    Args:
        since_last_n_days (int): The number of days from now to retrieve stats.

    Returns:
        dict: The platform statistics dictionary.

    """
    # Import here to avoid circular import within utils
    from dashboard.models import Bounty, BountyFulfillment

    last_n_days = datetime.now() - timedelta(days=since_last_n_days)
    bounties = Bounty.objects.current().filter(network='mainnet', created_on__gte=last_n_days)
    bounties = bounties.exclude(interested__isnull=True)
    total_bounties = bounties.count()
    completed_bounties = bounties.filter(idx_status__in=['done'])
    terminal_state_bounties = bounties.filter(idx_status__in=['done', 'expired', 'cancelled'])
    num_completed_bounties = completed_bounties.count()
    bounties_completion_percent = (num_completed_bounties / terminal_state_bounties.count()) * 100

    completed_bounties_fund = sum([
        bounty.value_in_usdt if bounty.value_in_usdt else 0
        for bounty in completed_bounties
    ])
    if num_completed_bounties:
        avg_fund_per_bounty = completed_bounties_fund / num_completed_bounties
    else:
        avg_fund_per_bounty = 0

    avg_fund_per_bounty = float('%.2f' % avg_fund_per_bounty)
    completed_bounties_fund = round(completed_bounties_fund)
    bounties_completion_percent = round(bounties_completion_percent)

    largest_bounty = Bounty.objects.current().filter(
        created_on__gte=last_n_days).order_by('-_val_usd_db').first()
    largest_bounty_value = largest_bounty.value_in_usdt

    bounty_fulfillments = BountyFulfillment.objects.filter(
        accepted_on__gte=last_n_days).order_by('-bounty__value_in_token')[:5]
    num_items = 10
    hunters = LeaderboardRank.objects.active().filter(leaderboard='quarterly_earners').order_by('-amount')[0:num_items].values_list('github_username', flat=True)

    # Overall transactions across the network are hard-coded for now
    total_transaction_in_usd = round(sum(
        [bounty.value_in_usdt for bounty in completed_bounties if bounty.value_in_usdt]
    ))
    total_transaction_in_eth = round(sum(
        [bounty.value_in_eth for bounty in completed_bounties if bounty.value_in_eth]) / 10**18
    )

    return {
        'total_funded_bounties': total_bounties,
        'bounties_completion_percent': bounties_completion_percent,
        'no_of_hunters': len(hunters),
        'num_completed_bounties': num_completed_bounties,
        'completed_bounties_fund': completed_bounties_fund,
        'avg_fund_per_bounty': avg_fund_per_bounty,
        'hunters': hunters,
        'largest_bounty': largest_bounty,
        'largest_bounty_value': largest_bounty_value,
        "total_transaction_in_usd": total_transaction_in_usd,
        "total_transaction_in_eth": total_transaction_in_eth,
    }


def func_name():
    """Determine the calling function's name.

    Returns:
        str: The parent method's name.

    """
    try:
        return sys._getframe(1).f_code.co_name
    except Exception as e:
        logger.error(e)
        return 'NA'
