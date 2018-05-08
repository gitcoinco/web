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

from django.conf import settings
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from marketing.models import EmailSubscriber, Stat
from slackclient import SlackClient
from slackclient.exceptions import SlackClientError

logger = logging.getLogger(__name__)


def get_stat(key):
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
        icon_url = 'https://gitcoin.co/static/v2/images/helmet.png'

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


def should_suppress_notification_email(email, _type='transactional'):
    queryset = EmailSubscriber.objects.filter(email__iexact=email)
    if queryset.exists():
        level = queryset.first().preferences.get('level', '')
        if _type in ['urgent', 'admin']:
            return False  # these email types are always sent
        if level == 'nothing':
            return True
        if level == 'lite1' and _type == 'transactional':
            return True
        if level == 'lite' and _type == 'roundup':
            return True
    return False


def get_or_save_email_subscriber(email, source, send_slack_invite=True, profile=None):
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
    except Exception as e:
        print(f'Failed to update or create email subscriber: ({email}) - {e}')
        return ''

    if created or not es.priv:
        es.set_priv()
        es.save()
        if send_slack_invite:
            invite_to_slack(email)

    return es
