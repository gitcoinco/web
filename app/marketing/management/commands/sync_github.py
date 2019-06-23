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
import datetime
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment, Interest, Profile, UserAction
from git.utils import get_user, repo_name
from marketing.models import GithubEvent

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'pulls github events associated with settings.GITHUB_REPO_NAME'
    all_bountied_repos_cache = None

    def all_bountied_repos(self):
        if self.all_bountied_repos_cache:
            return self.all_bountied_repos_cache

        bounties = Bounty.objects.current()
        return_me = []
        for bounty in bounties:
            try:
                org_name = bounty.org_name
                rn = repo_name(bounty.github_url)
                this_repo = f"{org_name}/{rn}".lower()
                if this_repo not in return_me:
                    return_me.append(this_repo)
            except Exception as e:
                print(e)
        self.all_bountied_repos_cache = return_me
        return return_me

    def do_we_care(self, event):
        repos_we_care_about = self.all_bountied_repos()
        try:
            repo_name = event.get('repo', {}).get('name', '').lower()
            return repo_name in repos_we_care_about
        except AttributeError:
            logger.debug('Error in do_we_care during sync_github')
            return False

    def sync_profile_actions(self):
        # figure out what github profiles we care about
        hours = 100 if settings.DEBUG else 24
        start = timezone.now() - timezone.timedelta(hours=hours)
        profile_ids_logged_in_last_time_period = list(UserAction.objects.filter(created_on__gt=start, action="Login").values_list('profile', flat=True))
        profile_ids_interest_last_time_period = list(Interest.objects.filter(created__gt=start).values_list('profile', flat=True))
        profile_ids_fulfilled_last_time_period = list(BountyFulfillment.objects.filter(created_on__gt=start).values_list('profile', flat=True))
        profile_ids = profile_ids_interest_last_time_period + profile_ids_logged_in_last_time_period + profile_ids_fulfilled_last_time_period
        profiles = Profile.objects.filter(pk__in=profile_ids)

        # process them
        for profile in profiles:
            try:
                events = get_user(profile.handle, '/events')
                for event in events:
                    try:
                        event_time = event.get('created_at', False)
                        created_on = datetime.datetime.strptime(event_time, '%Y-%m-%dT%H:%M:%SZ')
                    except Exception:
                        created_on = timezone.now()
                    if self.do_we_care(event):
                        GithubEvent.objects.get_or_create(
                            profile=profile,
                            payload=event,
                            what=event.get('type', ''),
                            repo=event.get('repo', {}).get('name', ''),
                            created_on=created_on,
                        )
            except Exception as e:
                logger.error('Error while syncing profile actions during sync_github', e)

    def sync_issue_comments(self):
        pass  # TODO: for each active github issue, it'd be great to pull down the comments / activity feed associatd with it

    def handle(self, *args, **options):
        self.sync_profile_actions()
        self.sync_issue_comments()
