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
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import pytz
from chat.tasks import get_driver
from dashboard.models import Profile

logger = logging.getLogger(__name__)



class Command(BaseCommand):
    help = "find users who are on chat and figure out their presence, save it to db"

    def add_arguments(self, parser):
        parser.add_argument(
            'seconds_back',
            default=99999999999,
            type=int,
            help="How many seconds back to look for presence"
        )


    def handle(self, *args, **options):
        # setup
        only_update_in_last_seconds_n = options['seconds_back']

        # connect to API
        d = get_driver()
        teams = d.teams.get_teams()

        for team in teams:

            # pull back users on team
            print(team['display_name'])
            all_users = []
            cont = True
            per_page = 60
            page = 0
            while cont:
                params = {'in_team':team['id'], 'sort':'last_activity_at', 'per_page': per_page, 'page': page}
                users = d.users.get_users(params=params)
                all_users += users
                cont = len(users) == per_page
                page += 1
            for user in users:
                pass

            # get through all users
            print(f"- {len(all_users)}")
            for user in all_users:
                last_activity_at = user['last_activity_at']
                username = user['username']
                timestamp = int(last_activity_at/1000)
                timestamp = timezone.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
                update_db = (timezone.now() - timestamp).seconds < only_update_in_last_seconds_n

                if update_db:
                    profile = Profile.objects.filter(handle__iexact=username).first()
                    if profile:
                        profile.last_chat_seen = timestamp
                        profile.chat_id = user['id']
                        profile.save()
