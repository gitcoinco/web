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

from django.core.management.base import BaseCommand

from dashboard.helpers import record_bounty_activity
from dashboard.models import Activity, Bounty, Interest
from dashboard.views import record_bounty_activity as record_bounty_activity_interest


def set_created(activity, date):
    if activity and date:
        activity.created = date
        activity.save()


def create_activities(bounty):
    act = record_bounty_activity('new_bounty', None, bounty)
    set_created(act, bounty.web3_created)
    approval_required = bounty.permission_type == 'approval'
    for interest in bounty.interested.all():
        event_name = 'start_work' if not approval_required else 'worker_applied'
        act = record_bounty_activity_interest(bounty, interest.profile.user, event_name, interest)
        set_created(act, interest.created)
        if approval_required and interest.status != Interest.STATUS_REVIEW:
            act = record_bounty_activity_interest(bounty, interest.profile.user, 'worker_approved', interest)
            set_created(act, interest.acceptance_date)
    done_recorded = False
    for fulfillment in bounty.fulfillments.all():
        act = record_bounty_activity('work_submitted', bounty.prev_bounty, bounty, fulfillment)
        set_created(act, fulfillment.created_on)
        if fulfillment.accepted:
            act = record_bounty_activity('work_done', bounty.prev_bounty, bounty, fulfillment)
            set_created(act, fulfillment.accepted_on)
            done_recorded = True
    if bounty.status == 'done' and not done_recorded:
        act = record_bounty_activity('work_done', bounty.prev_bounty, bounty)
        set_created(act, bounty.fulfillment_accepted_on)
    if bounty.status == 'cancelled':
        act = record_bounty_activity('killed_bounty', bounty.prev_bounty, bounty)
        set_created(act, bounty.canceled_on)


class Command(BaseCommand):

    help = 'creates activity records for current bounties'

    def add_arguments(self, parser):
        parser.add_argument(
            '-force', '--force',
            action='store_true',
            dest='force_refresh',
            default=False,
            help='Force the refresh'
        )

    def handle(self, *args, **options):
        force_refresh = options['force_refresh']
        if force_refresh:
            Activity.objects.all().delete()
        bounties = Bounty.objects.current()
        for bounty in bounties:
            if force_refresh or not bounty.activities.count():
                create_activities(bounty)
