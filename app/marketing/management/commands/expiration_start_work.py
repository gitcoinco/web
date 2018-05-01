'''
    Copyright (C) 2017 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import logging
import warnings
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import pytz
from dashboard.models import Bounty, Interest, UserAction
from dashboard.notifications import (
    maybe_notify_bounty_user_removed_to_slack, maybe_notify_bounty_user_warned_removed_to_slack,
    maybe_notify_user_removed_github, maybe_warn_user_removed_github,
)
from github.utils import get_interested_actions
from marketing.mails import bounty_startwork_expire_warning, bounty_startwork_expired

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def record_user_action(interest, event_name, last_heard_from_user_days):
    UserAction.objects.create(
        profile=interest.profile,
        action=event_name,
        metadata={
            'bounties': list(interest.bounty_set.values_list('pk', flat=True)),
            'interest_pk': interest.pk,
            'last_heard_from_user_days': last_heard_from_user_days,
        })


class Command(BaseCommand):

    help = 'lets a user know that they expressed interest in an issue and kicks them to do something about it'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print('not running start work expiration because DEBUG is on')
            return

        # TODO: DRY with dashboard/notifications.py
        num_days_back_to_warn = 3
        num_days_back_to_delete_interest = 6

        days = [i * 3 for i in range(1, 15)]
        days.reverse()
        if settings.DEBUG:
            days = range(1, 1000)
        for day in days:
            interests = Interest.objects.select_related('profile').filter(
                created__gte=(timezone.now() - timezone.timedelta(days=(day+1))),
                created__lt=(timezone.now() - timezone.timedelta(days=day)),
            )
            print(f'day {day} got {interests.count()} interests')
            for interest in interests:
                bounties = Bounty.objects.filter(
                    interested=interest,
                    current_bounty=True,
                    network='mainnet',
                    idx_status__in=['open', 'started']
                    )
                for bounty in bounties:
                    print("===========================================")
                    print(f"{interest} is interested in {bounty.pk} / {bounty.github_url}")
                    try:
                        actions = get_interested_actions(
                            bounty.github_url, interest.profile.handle, interest.profile.email)
                        should_warn_user = False
                        should_delete_interest = False
                        last_heard_from_user_days = None

                        if not actions:
                            should_warn_user = True
                            should_delete_interest = False
                            last_heard_from_user_days = (timezone.now() - interest.created).days
                            print(" - no actions")
                        else:
                            # example format: 2018-01-26T17:56:31Z'
                            action_times = [datetime.strptime(action['created_at'], '%Y-%m-%dT%H:%M:%SZ') for action in actions if action.get('created_at')]
                            last_action_by_user = max(action_times).replace(tzinfo=pytz.UTC)

                            # if user hasn't commented since they expressed interest, handled this condition
                            # per https://github.com/gitcoinco/web/issues/462#issuecomment-368384384
                            if last_action_by_user.replace() < interest.created:
                                last_action_by_user = interest.created

                            # some small calcs
                            delta_now_vs_last_action = timezone.now() - last_action_by_user
                            last_heard_from_user_days = delta_now_vs_last_action.days

                            # decide action params
                            should_warn_user = last_heard_from_user_days >= num_days_back_to_warn
                            should_delete_interest = last_heard_from_user_days >= num_days_back_to_delete_interest

                            print(f"- its been {last_heard_from_user_days} days since we heard from the user")

                        if should_delete_interest:
                            print(f'executing should_delete_interest for {interest.profile} / {bounty.github_url} ')

                            record_user_action(interest, 'bounty_abandonment_final', last_heard_from_user_days)

                            interest.delete()

                            # commenting on the GH issue
                            maybe_notify_user_removed_github(bounty, interest.profile.handle, last_heard_from_user_days)
                            # commenting in slack
                            maybe_notify_bounty_user_removed_to_slack(bounty, interest.profile.handle)
                            # send email
                            bounty_startwork_expired(interest.profile.email, bounty, interest, last_heard_from_user_days)

                        elif should_warn_user:

                            record_user_action(interest, 'bounty_abandonment_warning', last_heard_from_user_days)

                            print(f'executing should_warn_user for {interest.profile} / {bounty.github_url} ')
                            # commenting on the GH issue
                            maybe_warn_user_removed_github(bounty, interest.profile.handle, last_heard_from_user_days)
                            # commenting in slack
                            maybe_notify_bounty_user_warned_removed_to_slack(bounty, interest.profile.handle, last_heard_from_user_days)
                            # send email
                            bounty_startwork_expire_warning(interest.profile.email, bounty, interest, last_heard_from_user_days)

                    except Exception as e:
                        print(f'Exception in expiration_start_work.handle(): {e}')
