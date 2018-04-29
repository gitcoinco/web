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
from django.conf import settings

from marketing.models import EmailSubscriber, Stat
from slackclient import SlackClient


def get_stat(key):
    return Stat.objects.filter(key=key).order_by('-created_on').first().val


def invite_to_slack(email):
    if settings.DEBUG:
        return {}
    sc = SlackClient(settings.SLACK_TOKEN)
    response = sc.api_call('users.admin.invite', email=email)
    return response


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
