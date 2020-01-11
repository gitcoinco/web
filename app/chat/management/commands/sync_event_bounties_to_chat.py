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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from dashboard.models import Bounty, Interest, Profile
from chat.tasks import create_user, get_driver, create_channel, add_to_channel
import logging
from celery import group
from mattermostdriver.exceptions import (
    ResourceNotFound
)
logger = logging.getLogger(__name__)


def create_user_if_not_exists(profile):
    try:
        chat_driver = get_driver()

        current_chat_user = chat_driver.users.get_user_by_username(profile.handle)
        profile.chat_id = current_chat_user['id']
        profile.save()
        return False, current_chat_user
    except ResourceNotFound as RNF:
        new_user_request = create_user.apply_async(options={
            "email": profile.user.email,
            "username": profile.handle,
            "first_name": profile.user.first_name,
            "last_name": profile.user.last_name,
            "nickname": profile.handle,
            "auth_data": f'{profile.user.id}',
            "auth_service": "gitcoin",
            "locale": "en",
            "props": {},
            "notify_props": {
                "email": "false",
                "push": "mention",
                "desktop": "all",
                "desktop_sound": "true",
                "mention_keys": f'{profile.handle}, @{profile.handle}',
                "channel": "true",
                "first_name": "false"
            },
        }, params={
            "tid": settings.GITCOIN_HACK_CHAT_TEAM_ID
        })

        return True, new_user_request


class Command(BaseCommand):
    help = "Create channels for all active hackathon bounties"

    def handle(self, *args, **options):
        try:
            print(args)
            print(options)
            bounties_to_sync = Bounty.objects.filter(event_id__exact=options['event_id'])
            tasks = []

            for bounty in bounties_to_sync:

                profiles_to_connect = []

                funder_profile = Profile.objects.get(bounty.bounty_owner_github_username)

                if funder_profile is not None:
                    profiles_to_connect.append(funder_profile)
                    for interest in bounty.interested.all():
                        if interest.profile is not None:
                            if interest.profile.chat_id is None:
                                created, chat_user = create_user_if_not_exists(interest.profile)
                                interest.profile.chat_id = chat_user['id']
                                interest.profile.save()
                            profiles_to_connect.append(interest.profile.chat_id)
                    if bounty.chat_channel_id is None:
                        bounty_channel_name = slugify(f'{bounty.github_org_name}-{bounty.github_issue_number}')
                        bounty_channel_name = bounty_channel_name[:60]
                        create_channel_opts = {
                            'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                            'channel_display_name': f'{bounty_channel_name}-{bounty.title}'[:60],
                            'channel_name': bounty_channel_name[:60]
                        }
                        task = create_channel.s(create_channel_opts, link=add_to_channel.s(profiles_to_connect))
                    else:
                        task = add_to_channel.s(bounty.chat_channel_id, profiles_to_connect)

                    tasks.append(task)

            job = group(tasks)
            result = job.apply_async()
            print(result)
        except ConnectionError as exec:
            self.retry(30)
        except Exception as e:
            logger.error(str(e))
