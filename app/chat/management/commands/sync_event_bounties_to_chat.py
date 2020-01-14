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
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from dashboard.models import Bounty, Interest, Profile
from chat.tasks import create_user, get_driver, create_channel, add_to_channel
from chat.utils import create_user_if_not_exists, create_channel_if_not_exists
import logging
from celery import group

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create channels for all active hackathon bounties"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('event_id', type=int, help="The event ID to synchronize bounties and channels for")

    def handle(self, *args, **options):
        try:
            print(options['event_id'])
            bounties_to_sync = Bounty.objects.filter(
                Q(event__pk=options['event_id'])
            )
            tasks = []
            for bounty in bounties_to_sync:

                profiles_to_connect = []
                try:
                    funder_profile = Profile.objects.get(handle__iexact=bounty.bounty_owner_github_username.lower())
                except Exception as e:
                    print("here")
                    print(str(e))
                    continue

                if funder_profile is not None:
                    if funder_profile.chat_id is None:
                        created, funder_profile_request = create_user_if_not_exists(funder_profile)
                        funder_profile.chat_id = funder_profile_request['id']
                        funder_profile.save()
                    profiles_to_connect.append(funder_profile.chat_id)
                    for interest in bounty.interested.all():
                        if interest.profile is not None:
                            if interest.profile.chat_id is None:
                                created, chat_user = create_user_if_not_exists(interest.profile)
                                interest.profile.chat_id = chat_user['id']
                                interest.profile.save()
                            profiles_to_connect.append(interest.profile.chat_id)
                    if bounty.chat_channel_id is None or bounty.chat_channel_id is '':
                        bounty_channel_name = slugify(f'{bounty.github_org_name}-{bounty.github_issue_number}')
                        bounty_channel_name = bounty_channel_name[:60]
                        create_channel_opts = {
                            'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                            'channel_display_name': f'{bounty_channel_name}-{bounty.title}'[:60],
                            'channel_name': bounty_channel_name[:60]
                        }
                        task = create_channel.s(create_channel_opts, bounty.id)
                        task.link(add_to_channel.s(profiles_to_connect))
                    else:
                        task = add_to_channel.s(bounty.chat_channel_id, profiles_to_connect)

                    tasks.append(task)

            if len(tasks) > 0:
                job = group(tasks)
                result = job.apply_async()
            else:
                print("Nothing to Sync")

        except Exception as e:
            logger.error(str(e))
