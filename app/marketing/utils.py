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
from datetime import datetime, timedelta

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


def get_platform_wide_stats(since_last_n_days=90):
    """
    get platform wide stats for quarterly stats email
    """
    # Import here to avoid circular import within utils
    from dashboard.models import Bounty, BountyFulfillment, Profile

    last_n_days = datetime.now() - timedelta(days=since_last_n_days)
    bounties = Bounty.objects.stats_eligible().filter(created_on__gte=last_n_days)
    total_bounties = bounties.count()
    completed_bounties = bounties.filter(idx_status__in=['completed'])
    num_completed_bounties = completed_bounties.count()
    bounties_completion_percent = (num_completed_bounties / total_bounties) * 100

    completed_bounties_fund = sum([
        bounty.value_in_usdt if bounty.value_in_usdt else 0
        for bounty in completed_bounties
    ])
    if num_completed_bounties:
        avg_fund_per_bounty = completed_bounties_fund / num_completed_bounties
    else:
        avg_fund_per_bounty = 0

    largest_bounty = Bounty.objects.filter(created_on__gte=last_n_days).order_by('-value_in_token').first()

    bounty_fulfillments = BountyFulfillment.objects.filter(
        accepted_on__gte=last_n_days).order_by('-bounty__value_in_token')[:5]
    profiles = bounty_fulfillments.values_list('profile')
    hunters = Profile.objects.filter(id__in=profiles)
    hunters = [h.handle for h in hunters]

    # Overall transactions across the network are hard-coded for now
    total_transaction_in_usd = "132,810"
    total_transaction_in_dai = "20,000"
    total_transaction_in_eth = "812"
    total_transaction_in_wyv = "12,400"

    return {
        'total_funded_bounties': total_bounties,
        'bounties_completion_percent': bounties_completion_percent,
        'no_of_hunters': len(hunters),
        'num_completed_bounties': num_completed_bounties,
        'completed_bounties_fund': completed_bounties_fund,
        'avg_fund_per_bounty': avg_fund_per_bounty,
        'hunters': hunters,
        'largest_bounty': largest_bounty,
        "total_transaction_in_usd": total_transaction_in_usd,
        "total_transaction_in_dai": total_transaction_in_dai,
        "total_transaction_in_eth": total_transaction_in_eth,
        "total_transaction_in_wyv": total_transaction_in_wyv
    }
