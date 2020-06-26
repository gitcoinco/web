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
from app.redis_service import RedisService
from chat.tasks import get_driver
from dashboard.models import Profile
from django_bulk_update.helper import bulk_update

logger = logging.getLogger(__name__)



class Command(BaseCommand):
    help = "find users who are on chat and figure out their presence, save it to db"


    def handle(self, *args, **options):
        # connect to API
        d = get_driver()
        teams = d.teams.get_teams()

        # connect to redis
        redis = RedisService().redis

        # outer vars
        all_usernames = []
        all_user_statuses = {}
        all_response = []

        for team in teams:
            if team['display_name'] == 'Codefund':
                continue

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
                #for testing on small amount of data
                #if settings.DEBUG:
                #    cont = False
            for user in users:
                pass

            # get through all users
            print(f"- {len(all_users)}")
            users_status = d.client.post('/users/status/ids', [ele['id'] for ele in all_users])
            all_response += users_status
            users_status_by_id = { ele['user_id']: ele for ele in users_status }
            all_usernames += [ele['username'].lower() for ele in all_users]

            # iterate through each one, and sync it to our DB
            for user in all_users:
                last_activity_at_1 = user['last_activity_at']
                last_activity_at_2 = users_status_by_id[user['id']]['last_activity_at']
                status = users_status_by_id[user['id']]['status']
                last_activity_at = max(last_activity_at_2, last_activity_at_1)
                username = user['username']
                timestamp = int(last_activity_at/1000)
                timestamp = timezone.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
                all_user_statuses[username] = (status, timestamp, user['id'])

            # look for manual statuses set by /api/v0.1/chat route and clean them up if needed
            for ele in all_response:

                user_id = ele['user_id']
                status = ele['status']
                if status == 'offline':
                    continue

                # user has been offline for 10 mins
                # update mattermost, and redis
                max_delta = (10*60)

                # calc it
                now = timezone.now().timestamp()
                last_action_mattermost = int(ele['last_activity_at']/1000)
                redis_response = redis.get(user_id)
                last_seen_gc = int(float(redis_response)) if redis_response else now

                # do update
                is_away_mm = ((now - last_action_mattermost) > max_delta)
                is_away_gc = (now - last_seen_gc) > max_delta
                manual = ele['manual']
                update_ele = (manual and is_away_gc) or (not manual and is_away_mm)
                if update_ele or settings.DEBUG:
                    new_status = 'offline' 
                    d.client.put(f'/users/{user_id}/status', {'user_id': user_id, 'status': new_status})
                    redis.set(user_id, 0)
        
        # update all chat ids not in DB
        profiles = Profile.objects.filter(handle__in=all_usernames, chat_id='')
        for profile in profiles:
            _, _, profile.chat_id = all_user_statuses[profile.handle]
        bulk_update(profiles, update_fields=['chat_id'])  

        # update all chat info that is in redis
        # all_user_statuses[username] = (status, timestamp, user['id'])
        for username, ele in all_user_statuses.items():
            key = f"chat:{ele[2]}"
            redis.set(key, ele[0])
