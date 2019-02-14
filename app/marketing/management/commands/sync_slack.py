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
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from marketing.models import SlackPresence, SlackUser
from slackclient import SlackClient


class Command(BaseCommand):

    help = 'pulls slack presence'

    def handle(self, *args, **options):
        sc = SlackClient(settings.SLACK_TOKEN)
        ul = sc.api_call("users.list")
        user = ul['members'][0]

        num_active = 0
        num_away = 0
        total = 0
        start_time = time.time()
        for user in ul['members']:
            try:
                # manage making request and still respecting rate limit
                should_do_request = True
                is_rate_limited = False
                while should_do_request:
                    response = sc.api_call("users.getPresence", user=user['id'])
                    is_rate_limited = response.get('error', None) == 'ratelimited'
                    should_do_request = is_rate_limited
                    if is_rate_limited:
                        time.sleep(2)
                        print('-- rate limited.. waiting')

                # figure out the slack users' presence
                pres = response.get('presence', None)
                if pres == 'active':
                    num_active += 1
                if pres == 'away':
                    num_away += 1
                total += 1
                if total % 30 == 0:
                    rate_per_sec = round(total / (time.time() - start_time), 2)
                    print(f"[{total}]processing {rate_per_sec} lookups /sec")

                # save user by user 'lastseen' info
                username = user['profile']['display_name']
                email = user['profile']['email']
                # print(username, email)
                su, _ = SlackUser.objects.get_or_create(
                    username=username,
                    email=email,
                    defaults={
                        'profile': user['profile'],
                    }
                    )
                if pres == 'active':
                    su.last_seen = timezone.now()
                    su.times_seen += 1
                    # 3/8/2017
                    # to manage the scale of the DB, a SlackUser will be assumbed to be
                    # away unless a SlackPresence Object exists
                    SlackPresence.objects.create(
                        slackuser=su,
                        status=pres,
                        )

                else:
                    su.last_unseen = timezone.now()
                    su.times_unseen += 1
                su.save()
            except Exception as e:
                print(e)
        print("DONE at {}".format(timezone.now().strftime("%Y-%m-%d %H:%M")))
