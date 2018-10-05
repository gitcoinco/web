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
import datetime
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import BountyFulfillment
from git.utils import get_gh_issue_state, get_interested_actions, post_issue_comment
from marketing.mails import funder_payout_reminder
from dashboard.utils import record_funder_inaction_on_fulfillment


class Command(BaseCommand):

    help = 'pulls github events associated with settings.GITHUB_REPO_NAME'

    def add_arguments(self, parser):
        parser.add_argument(
            '-live', '--live',
            action='store_true',
            dest='live',
            default=False,
            help='Actually Send the emails'
        )

    # ->-> Check if the referenced pull request:
    # ->--> Has been merged
    # ->--> Occurred before the issue was Closed by anyone, like a maintainer
    # Use the github API to look for PullRequestEVent
    def sync_pull_requests_with_bounty_fulfillments(self, options):
        # This is the subset of profile IDs to be saved for PullRequest Eents in the GitHub Events API
        hours = 500 if settings.DEBUG else 24
        start = timezone.now() - timezone.timedelta(hours=hours)
        deadline = timezone.now() - timezone.timedelta(hours=hours*3)
        escalated_deadline = deadline - timezone.timedelta(hours=hours*3)
        print(hours, start)

        #  Sync actions for Git issues that are in bounties that:
        bounties_fulfilled_last_time_period = list(BountyFulfillment.objects.filter(accepted=False).filter(created_on__gt=start).values_list('pk', flat=True))
        fulfillments_notified_before_last_time_period = list(BountyFulfillment.objects.filter(accepted=False).filter(funder_last_notified_on__lt=start).values_list('pk', flat=True))
        bounty_fulfillments = bounties_fulfilled_last_time_period + fulfillments_notified_before_last_time_period

        bounty_fulfillments = BountyFulfillment.objects.filter(pk__in=bounty_fulfillments)
        for bounty_fulfillment in bounty_fulfillments:
            # Debug
            # May not be necessary if these are arleady synced
            # bounty_gh_details = get_gh_issue_details() 
            print(bounty_fulfillment.bounty)
            bounty = bounty_fulfillment.bounty
            closed_issue = get_gh_issue_state(bounty.github_org_name, bounty.github_repo_name, bounty.github_issue_number)
            print(closed_issue)
            if (closed_issue == 'closed'):
                print(bounty.github_url)
                actions = get_interested_actions(bounty.github_url, '*')
                # -> retreive:
                # --> The pull request that references the issue that a BountyFulfillment points to
                pr_ref_commit_url = None
                pr_merged_commit_url = None
                for action in actions:
                    print(action)
                    if action['event'] == 'referenced':
                        print(action['commit_url'])
                        pr_ref_commit_url = action['commit_url']
                    elif action['event'] == 'merged':
                        print(action['commit_url'])
                        pr_merged_commit_url = action['commit_url']
                notified = None
                if pr_ref_commit_url and pr_merged_commit_url:
                    if pr_ref_commit_url == pr_merged_commit_url:
                        try:
                            notified = self.notify_funder(bounty.bounty_owner_email, bounty, bounty_fulfillment.fulfiller_github_username, options['live'])
                            if bounty_fulfillment.created_on < deadline:
                                post_issue_comment(
                                    bounty.github_org_name, bounty.gihtub_repo_name, bounty.github_issue_number, 
                                    '@'+bounty.bounty_owner_github_username+', please remember to close out the bounty!'
                                )
                                if bounty_fulfillment.created_on < escalated_deadline:
                                    record_funder_inaction_on_fulfillment(bounty_fulfillment)
                            print('Sending payment reminder: ')
                            print(bounty.github_org_name + '/' + bounty.github_repo_name + ' ' + str(bounty.github_issue_number))
                            if(notified):
                                print('.\n Emailed.')
                            else:
                                print('.\n Email failed.')

                        except Exception as e:
                            print(e)
                            time.sleep(5)

                if notified:
                    bounty_fulfillment.funder_last_notified_on = timezone.now()
                    bounty_fulfillment.save()


    def notify_funder(self, to_email, bounty, github_username, live):
        return funder_payout_reminder(to_email=to_email, bounty=bounty, github_username=github_username, live=live)

    def handle(self, *args, **options):
        self.sync_pull_requests_with_bounty_fulfillments(options)

