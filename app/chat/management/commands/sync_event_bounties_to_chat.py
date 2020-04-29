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
from django.db.models import Q
from django.utils.text import slugify

from celery import group
from chat.tasks import (
    add_to_channel, associate_chat_to_profile, create_channel, create_channel_if_not_exists, create_user, get_driver,
)
from dashboard.models import Bounty, Interest, Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create channels for all active hackathon bounties"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('event_id', type=int, help="The event ID to synchronize bounties and channels for")

    def handle(self, *args, **options):
        try:
            bounties_to_sync = Bounty.objects.filter(
                Q(event__pk=options['event_id'])
            )
            tasks = []
            for bounty in bounties_to_sync:
                profiles_to_connect = []
                try:
                    funder_profile = Profile.objects.get(handle=bounty.bounty_owner_github_username.lower())

                    if funder_profile:
                        if funder_profile.chat_id:
                            created, funder_profile = associate_chat_to_profile(funder_profile)
                        profiles_to_connect.append(funder_profile.chat_id)
                        for interest in bounty.interested.all():
                            if interest.profile:
                                if interest.profile.chat_id:
                                    created, interest.profile = associate_chat_to_profile(interest.profile)
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
                            task = add_to_channel.s({'id': bounty.chat_channel_id}, profiles_to_connect)
                        tasks.append(task)
                except Exception as e:
                    logger.error(str(e))
                    continue
            if len(tasks) > 0:
                job = group(tasks)
                result = job.apply_async()
            else:
                print("Nothing to Sync")

        except Exception as e:
            logger.error(str(e))
