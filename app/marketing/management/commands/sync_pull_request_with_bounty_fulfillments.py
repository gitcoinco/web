'''
    Copyright (C) 2019 Gitcoin Core

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
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import BountyFulfillment
from dashboard.utils import record_funder_inaction_on_fulfillment
from git.utils import get_gh_issue_state, get_interested_actions, post_issue_comment
from marketing.mails import funder_payout_reminder

logger = logging.getLogger('')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%name)s - %(levelname)s - %(message)s'))
logger.addHandler(console)


class Command(BaseCommand):

    help = 'pulls github pull request event associated with unaccepted BountyFulfillments'
    help += ' then notifies the funder by email the issue is open awaiting their review.'
    help += ' Also escalates bounties that are being held open even with an accepted PR.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-live', '--live', action='store_true', dest='live', default=False, help='Actually Send the emails'
        )

    def _get_time_window(self, timestamp, settings):
        # This is the subset of profile IDs to be saved for PullRequest events in the GitHub Events API
        hours = 500 if settings.DEBUG else 24
        start = timezone.now() - timezone.timedelta(hours=hours)
        deadline = timezone.now() - timezone.timedelta(hours=hours * 3)
        escalated_deadline = deadline - timezone.timedelta(hours=hours * 3)
        return hours, start, deadline, escalated_deadline

    def _check_if_bounty_is_closed(self, bounty):
        try:
            closed_issue = get_gh_issue_state(
                bounty.github_org_name, bounty.github_repo_name, bounty.github_issue_number
            )
        except Exception as e:
            logger.warning(e)
            return False
        return closed_issue == 'closed'

    def _get_pr_urls(self, actions, cross_referenced_action_github_username):
        pr_ref_commit_url = None
        pr_merged_commit_url = None
        for cross_referenced_action in actions:
            if cross_referenced_action['event'] == 'cross-referenced':
                if cross_referenced_action['actor']['login'] == cross_referenced_action_github_username:
                    for referenced_action in actions:
                        if referenced_action['event'] == 'referenced':
                            if cross_referenced_action['pr_url'] == referenced_action['pr_url']:
                                pr_ref_commit_url = referenced_action['commit_url']
            elif cross_referenced_action['event'] == 'merged':
                pr_merged_commit_url = cross_referenced_action['commit_url']

        return pr_ref_commit_url, pr_merged_commit_url

    def _notify_funder(self, bounty, bounty_fulfillment, live, deadline, escalated_deadline):
        try:
            notified = funder_payout_reminder(
                to_email=bounty.bounty_owner_email,
                bounty=bounty,
                github_username=bounty_fulfillment.fulfiller_github_username,
                live=live
            )
            if bounty_fulfillment.created_on < deadline:
                logger.info('Posting github comment')
                try:
                    post_issue_comment(
                        bounty.github_org_name, bounty.github_repo_name, bounty.github_issue_number,
                        '@' + bounty.bounty_owner_github_username + ', please remember to close out the bounty!'
                    )
                except Exception as e:
                    logger.warning(e)

                if bounty_fulfillment.created_on < escalated_deadline:
                    record_funder_inaction_on_fulfillment(bounty_fulfillment)
            logger.info('Sending payment reminder: ')
            logger.info(bounty.github_org_name + '/' + bounty.github_repo_name + ' ' + str(bounty.github_issue_number))
            return notified

        except Exception as e:
            logger.warning(e)

    # ->-> Check if the referenced pull request:
    # ->--> Has been merged
    # ->--> Occurred before the issue was Closed by anyone, like a maintainer
    # Use the github API to look for PullRequestEVent
    def sync_pull_requests_with_bounty_fulfillments(self, options):
        self.options = options
        hours, start, deadline, escalated_deadline = self._get_time_window(timezone.now(), settings)
        #  Sync actions for Git issues that are in bounties that:
        bounties_fulfilled = BountyFulfillment.objects.filter(accepted=False)
        bounties_fulfilled_last_time_period = bounties_fulfilled.filter(created_on__gt=start)
        fulfillments_notified_before_last_time_period = bounties_fulfilled.filter(funder_last_notified_on__lt=start)
        bounty_fulfillments = bounties_fulfilled_last_time_period | fulfillments_notified_before_last_time_period
        bounty_fulfillments = bounty_fulfillments.distinct()
        for bounty_fulfillment in bounty_fulfillments:
            bounty = bounty_fulfillment.bounty
            if (self._check_if_bounty_is_closed(bounty)):
                try:
                    actions = get_interested_actions(bounty.github_url, '*')
                except Exception as e:
                    logger.warning(e)
                    continue
                # -> retreive:
                # --> The pull request that references the issue that a BountyFulfillment points to

                pr_ref_commit_url, pr_merged_commit_url = self._get_pr_urls(actions, bounty_fulfillment.fulfiller_github_username)
                if pr_ref_commit_url and pr_merged_commit_url:
                    if pr_ref_commit_url == pr_merged_commit_url:
                        if self._notify_funder(
                            bounty, bounty_fulfillment, self.options['live'], deadline, escalated_deadline
                        ):
                            bounty_fulfillment.funder_last_notified_on = timezone.now()
                            bounty_fulfillment.save()
                        else:
                            logger.warning('Email failed')

    def handle(self, *args, **options):
        self.sync_pull_requests_with_bounty_fulfillments(options)
