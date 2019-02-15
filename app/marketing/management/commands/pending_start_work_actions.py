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

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Interest
from dashboard.views import record_user_action
from marketing.mails import start_work_applicant_about_to_expire, start_work_applicant_expired, start_work_approved

THRESHOLD_HOURS_AUTO_APPROVE = 3 * 24
THRESHOLD_HOURS_AUTO_APPROVE_WARNING = 2 * 24

logger = logging.getLogger(__name__)


def start_work_applicant_expired_executer(interest, bounty):

    start_work_approved(interest, bounty)
    start_work_applicant_expired(interest, bounty)
    interest.pending = False
    interest.acceptance_date = timezone.now()
    interest.save()
    record_user_action(interest.profile.user, 'worker_approved', bounty)


def helper_execute(threshold, func_to_execute, action_str):
    start_time = timezone.now() - timezone.timedelta(hours=(threshold+1))
    end_time = timezone.now() - timezone.timedelta(hours=(threshold))
    interests = Interest.objects.filter(pending=True, created__gt=start_time, created__lt=end_time)
    print(f"{interests.count()} {action_str}")
    for interest in interests:
        bounty = interest.bounties.first()
        if bounty:
            has_approved_worker_already = bounty.interested.filter(pending=False).exists()
            if bounty.admin_override_suspend_auto_approval:  # skip bounties where this flag is set
                print("skipped bc of admin_override_suspend_auto_approval")
                continue
            if has_approved_worker_already:
                print("skipped bc of has_approved_worker_already")
                continue
            is_bounty_in_terminal_state = bounty.status in Bounty.TERMINAL_STATUSES
            is_bounty_already_submitted = bounty.status == 'submitted'
            if is_bounty_in_terminal_state or is_bounty_already_submitted:
                print("skipped bc of is_bounty_in_terminal_state | is_bounty_already_submitted")
                continue

            print(f"- {interest.pk} {action_str}")
            func_to_execute(interest, bounty)
        else:
            logger.error(f'Interest: {interest} missing bounty')


class Command(BaseCommand):

    help = 'handles pending start work actions for https://github.com/gitcoinco/web/pull/1098'

    def handle(self, *args, **options):

        # warnings
        helper_execute(THRESHOLD_HOURS_AUTO_APPROVE_WARNING, start_work_applicant_about_to_expire, 'warning')

        # auto approval
        helper_execute(THRESHOLD_HOURS_AUTO_APPROVE, start_work_applicant_expired_executer, 'auto approval')
