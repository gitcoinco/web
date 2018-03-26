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

from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Interest
from github.utils import get_issue_timeline_events, issue_number, org_name, repo_name
from marketing.mails import bounty_startwork_expire_warning, bounty_startwork_expired


class Command(BaseCommand):

    help = 'lets a user know that they expressed interest in an issue and kicks them to do something about it'

    def handle(self, *args, **options):

        if settings.DEBUG:
            print('not running bc DEBUG is on')
            return

        num_days_back_to_warn = 3
        num_days_back_to_delete_interest = 7
        # Define which timeline events demonstrate that the user is still interested in working on the issue
        # See https://developer.github.com/v3/issues/timeline/ for list of possible event types.
        activity_event_types = ['commented', 'cross-referenced', 'merged', 'referenced', 'review_requested']

        days = [i * 3 for i in range(1, 15)]
        if settings.DEBUG:
            days = range(1, 1000)
        for day in days:
            interests = Interest.objects.filter(
                created__gte=(timezone.now() - timezone.timedelta(days=(day+1))),
                created__lt=(timezone.now() - timezone.timedelta(days=day)),
            ).all()
            print('day {} got {} interests'.format(day, interests.count()))
            for interest in interests:
                for bounty in Bounty.objects.filter(interested=interest, current_bounty=True, idx_status__in=['open', 'started']):
                    print("{} is interested in {}".format(interest, bounty))
                    try:
                        owner = org_name(bounty.github_url)
                        repo = repo_name(bounty.github_url)
                        issue_num = issue_number(bounty.github_url)
                        timeline = get_issue_timeline_events(owner, repo, issue_num)
                        actions_by_interested_party = []

                        for action in timeline:
                            gh_user = None
                            # GitHub might populate actor OR user OR neither for some events
                            if 'actor' in action:
                                gh_user = action['actor']['login']
                            elif 'user' in action:
                                gh_user = action['user']['login']

                            if gh_user == interest.profile.handle and action['event'] in activity_event_types:
                                actions_by_interested_party.append(action)
                        should_warn_user = False
                        should_delete_interest = False
                        last_heard_from_user_days = None

                        if len(actions_by_interested_party) == 0:
                            should_warn_user = True
                            should_delete_interest = False
                        else:
                            # example format: 2018-01-26T17:56:31Z'
                            action_times = [datetime.strptime(action['created_at'], '%Y-%m-%dT%H:%M:%SZ') for action in actions_by_interested_party]
                            last_action_by_user = max(action_times)

                            # if user hasn't commented since they expressed interest, handled this condition
                            # per https://github.com/gitcoinco/web/issues/462#issuecomment-368384384
                            if last_action_by_user < interest.created.replace(tzinfo=None):
                                last_action_by_user = interest.created.replace(tzinfo=None)

                            # some small calcs
                            delta_now_vs_last_action = datetime.now() - last_action_by_user
                            last_heard_from_user_days = delta_now_vs_last_action.days

                            # decide action params
                            should_warn_user = last_heard_from_user_days >= num_days_back_to_warn
                            should_delete_interest = last_heard_from_user_days >= num_days_back_to_delete_interest

                            print(f"- its been {last_heard_from_user_days} days since we heard from the user")

                        if should_delete_interest:
                            print('executing should_delete_interest for {}'.format(interest.pk))
                            bounty_startwork_expired(interest.profile.email, bounty, interest, last_heard_from_user_days)
                            interest.delete()

                        elif should_warn_user:
                            print('executing should_warn_user for {}'.format(interest.pk))
                            bounty_startwork_expire_warning(interest.profile.email, bounty, interest, last_heard_from_user_days)

                    except Exception as e:
                        print(f'Exception in expiration_start_work.handle(): {e}')
