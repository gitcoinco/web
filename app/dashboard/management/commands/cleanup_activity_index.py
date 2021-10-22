'''
    Copyright (C) 2021 Gitcoin Core

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

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from dashboard.models import Activity, ActivityIndex


class Command(BaseCommand):

    help = 'cleans up activity index older than 400 days'

    def handle(self, *args, **options):
        purge_activity_index = timezone.now() - timedelta(days=400)
        ActivityIndex.objects.filter(created_on__lt=purge_activity_index).delete()
        print('deleted')



def port_activity_to_index():
    '''
        USEAGE: To be run to port data from activity from activity index
        NOTE: REMEMBER THIS COMMAND ALSO CLEARS ACTIVITY INDEX
    '''

    # clear ActivityIndex
    ActivityIndex.objects.all().delete()


    # fetch last n days activity to be ingested to ActivityIndex
    _400days= timezone.now() - timedelta(days=400)

    activities= Activity.objects.filter(created_on__gt=_400days).order_by('created_on')

    # Grants Activities
    grants_activity_query = (
        Q(activity_type='new_grant')
        | Q(activity_type='update_grant')
        | Q(activity_type='killed_grant')
        # | Q(activity_type='negative_contribution')
        | Q(activity_type='new_grant_contribution')
        | Q(activity_type='new_grant_subscription')
        # | Q(activity_type='killed_grant_contribution')
        | Q(activity_type='flagged_grant')
    )

    # Kudos Activities
    kudos_activity_query = (
        Q(activity_type='new_kudos')
        | Q(activity_type='created_kudos')
        | Q(activity_type='receive_kudos')
    )

    # Quests Activities
    quests_activity_query = (
        Q(activity_type='played_quest')
        | Q(activity_type='beat_quest')
        | Q(activity_type='created_quest')
    )

    # Tips Activities
    tip_activity_query = (
        Q(activity_type='new_tip')
        | Q(activity_type='receive_tip')
    )

    # Profile Activities
    profile_activity_query = (
        Q(activity_type='joined')
        # | Q(activity_type='updated_avatar')
        # | Q(activity_type='mini_clr_payout')
        | Q(activity_type='wall_post')
        | Q(activity_type='status_update')
    )

    # Hacks/Bounties Activities
    hackathon_activity_query = (
        Q(activity_type='hackathon_registration')
        | Q(activity_type='hackathon_new_hacker')
        | Q(activity_type='hypercharge_bounty')
        | Q(activity_type='new_bounty')
        | Q(activity_type='start_work')
        | Q(activity_type='stop_work')
        | Q(activity_type='work_submitted')
        | Q(activity_type='work_done')
        | Q(activity_type='worker_approved')
        | Q(activity_type='worker_rejected')
        | Q(activity_type='worker_applied')
        | Q(activity_type='increased_bounty')
        | Q(activity_type='killed_bounty')
        | Q(activity_type='bounty_abandonment_escalation_to_mods')
        | Q(activity_type='bounty_abandonment_warning')
        | Q(activity_type='bounty_removed_slashed_by_staff')
        | Q(activity_type='bounty_removed_by_staff')
        | Q(activity_type='bounty_removed_by_funder')
        | Q(activity_type='new_crowdfund')
    )

    # Platform Activities
    platform_activity_query = (
        Q(activity_type='leaderboard_rank')
        | Q(activity_type='consolidated_leaderboard_rank')
        # | Q(activity_type='consolidated_mini_clr_payout')
    )


    # helper function to populate grant activity index
    def populate_grants_activity_index(activities):
        for _activity in activities:
            _activity.populate_activity_index()


    # helper function to populate kudos activity index
    def populate_kudos_activity_index(activities):
        for _activity in activities:
            _activity.populate_activity_index()


    # helper function to populate quests activity index
    def populate_quests_activity_index(activities):
        for _activity in activities:
            _activity.populate_activity_index()

    
    # helper function to populate tips activity index
    def populate_tips_activity_index(activities):
        for _activity in activities:
            _activity.populate_activity_index()

    
    # helper function to populate profiles activity index
    def populate_profiles_activity_index(activities):
        for _activity in activities:
            _activity.populate_activity_index()


    # helper function to populate platform activity index
    def populate_platforms_activity_index(activities):
        for _activity in activities:
            _activity.populate_platform_activity_index()


    # helper function to populate platform activity index
    def populate_hackathons_activity_index(activities):
        for _activity in activities:
            _activity.populate_activity_index()


    _activities = activities.filter(quests_activity_query)
    populate_quests_activity_index(_activities)
    print('quests activity indexed')

    _activities = activities.filter(kudos_activity_query)
    populate_kudos_activity_index(_activities)
    print('kudos activity indexed')

    _activities = activities.filter(tip_activity_query)
    populate_tips_activity_index(_activities)
    print('tips activity indexed')

    _activities = activities.filter(profile_activity_query)
    populate_profiles_activity_index(_activities)
    print('profiles activity indexed')
    
    _activities = activities.filter(platform_activity_query)
    populate_platforms_activity_index(_activities)
    print('platform activity indexed')

    _activities = activities.filter(hackathon_activity_query)
    populate_hackathons_activity_index(_activities)
    print('hackathons activity indexed')

    _activities = activities.filter(grants_activity_query)
    populate_grants_activity_index(_activities)
    print('grants activity indexed')
