'''
    Copyright (C) 2019 Gitcoin Core

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
from django.db.models import Q
from django.utils import timezone

import pytz
from dashboard.models import Bounty, Interest, UserAction
from dashboard.notifications import (
    maybe_notify_bounty_user_escalated_to_slack, maybe_notify_bounty_user_warned_removed_to_slack,
    maybe_notify_user_escalated_github, maybe_warn_user_removed_github,
)
from dashboard.utils import record_user_action_on_interest
from git.utils import get_interested_actions
from marketing.mails import bounty_startwork_expire_warning, bounty_startwork_expired

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Command(BaseCommand):

    help = 'lets a user know that they expressed interest in an issue and kicks them to do something about it'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print('not running start work expiration because DEBUG is on')
            return

        # TODO: DRY with dashboard/notifications.py
        num_days_back_to_warn = 3
        num_days_back_to_delete_interest = 6
        num_days_back_to_ignore_bc_mods_got_it = 9

        days = [i * 3 for i in range(1, 15)]
        days.reverse()
        if settings.DEBUG:
            days = range(1, 1000)
        for day in days:
            start_date = (timezone.now() - timezone.timedelta(days=(day+1)))
            end_date = (timezone.now() - timezone.timedelta(days=day))

            interests = Interest.objects.select_related("profile").filter(
                Q(created__gte=start_date, created__lt=end_date) |
                Q(acceptance_date__gte=start_date, acceptance_date__lt=end_date),
                pending=False
            ).distinct('pk')

            print(f'day {day} got {interests.count()} interests')
            for interest in interests:

                if interest.acceptance_date:
                    interest_day_0 = interest.acceptance_date
                    bounties = Bounty.objects.current().filter(
                        interested=interest,
                        project_type='traditional',
                        network='mainnet',
                        idx_status__in=['open', 'started'],
                        permission_type='approval',
                    )
                else:
                    interest_day_0 = interest.created
                    bounties = Bounty.objects.current().filter(
                        interested=interest,
                        project_type='traditional',
                        network='mainnet',
                        idx_status__in=['open', 'started'],
                        permission_type='permissionless',
                    )

                for bounty in bounties:
                    print("===========================================")
                    print(f"{interest} is interested in {bounty.pk} / {bounty.github_url}")
                    try:
                        actions = get_interested_actions(
                            bounty.github_url, interest.profile.handle, interest.profile.email
                        )
                        should_warn_user = False
                        should_delete_interest = False
                        should_ignore = False
                        last_heard_from_user_days = None

                        if not actions:
                            should_warn_user = True
                            should_delete_interest = False
                            last_heard_from_user_days = (timezone.now() - interest_day_0).days
                            print(" - no actions")
                        else:
                            # example format: 2018-01-26T17:56:31Z'
                            action_times = [
                                datetime.strptime(action['created_at'], '%Y-%m-%dT%H:%M:%SZ') for action in actions
                                if action.get('created_at')
                            ]
                            last_action_by_user = max(action_times).replace(tzinfo=pytz.UTC)

                            # if user hasn't commented since they expressed interest, handled this condition
                            # per https://github.com/gitcoinco/web/issues/462#issuecomment-368384384
                            if last_action_by_user.replace() < interest_day_0:
                                last_action_by_user = interest_day_0

                            # some small calcs
                            snooze_time = timezone.timedelta(days=bounty.snooze_warnings_for_days)
                            delta_now_vs_last_action = timezone.now() - snooze_time - last_action_by_user
                            last_heard_from_user_days = delta_now_vs_last_action.days

                            # decide action params
                            should_warn_user = last_heard_from_user_days >= num_days_back_to_warn
                            should_delete_interest = last_heard_from_user_days >= num_days_back_to_delete_interest
                            should_ignore = last_heard_from_user_days >= num_days_back_to_ignore_bc_mods_got_it

                            print(f"- its been {last_heard_from_user_days} days since we heard from the user")
                        if should_ignore:
                            print(f'executing should_ignore for {interest.profile} / {bounty.github_url} ')

                        elif should_delete_interest:
                            print(f'executing should_delete_interest for {interest.profile} / {bounty.github_url} ')
                            interest = interest.mark_for_review()

                            record_user_action_on_interest(
                                interest, 'bounty_abandonment_escalation_to_mods', last_heard_from_user_days
                            )

                            # commenting on the GH issue
                            maybe_notify_user_escalated_github(
                                bounty, interest.profile.handle, last_heard_from_user_days
                            )

                            # commenting in slack
                            maybe_notify_bounty_user_escalated_to_slack(
                                bounty, interest.profile.handle, last_heard_from_user_days
                            )

                            # send email
                            bounty_startwork_expired(
                                interest.profile.email, bounty, interest, last_heard_from_user_days
                            )

                        elif should_warn_user:
                            record_user_action_on_interest(
                                interest, 'bounty_abandonment_warning', last_heard_from_user_days
                            )

                            print(f'executing should_warn_user for {interest.profile} / {bounty.github_url} ')

                            # commenting on the GH issue
                            maybe_warn_user_removed_github(bounty, interest.profile.handle, last_heard_from_user_days)

                            # commenting in slack
                            maybe_notify_bounty_user_warned_removed_to_slack(
                                bounty, interest.profile.handle, last_heard_from_user_days
                            )

                            # send email
                            bounty_startwork_expire_warning(
                                interest.profile.email, bounty, interest, last_heard_from_user_days
                            )
                    except Exception as e:
                        print(f'Exception in expiration_start_work.handle(): {e}')
