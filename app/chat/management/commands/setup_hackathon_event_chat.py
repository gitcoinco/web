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
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.text import slugify
from celery import group
from chat.tasks import add_to_channel, create_channel, create_user, get_driver
from chat.utils import create_channel_if_not_exists, associate_chat_to_profile
from dashboard.models import HackathonEvent, HackathonRegistration, Interest, Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create channels for hackathons"

    def handle(self, *args, **options):
        try:
            tasks = []

            hackathons_to_sync = HackathonEvent.objects.all()

            for hackathon in hackathons_to_sync:
                channels_to_connect = []
                if not hackathon.chat_channel_id:
                    created, channel_details = create_channel_if_not_exists({
                        'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                        'channel_display_name': f'general-{hackathon.slug}'[:60],
                        'channel_name': f'general-{hackathon.name}'[:60]
                    })
                    hackathon.chat_channel_id = channel_details['id']
                    hackathon.save()
                channels_to_connect.append(hackathon.chat_channel_id)
                regs_to_sync = HackathonRegistration.objects.filter(hackathon=hackathon)
                profiles_to_connect = []
                for reg in regs_to_sync:
                    if reg.registrant and not reg.registrant.chat_id:
                        created, reg.registrant = associate_chat_to_profile(reg.registrant)
                    profiles_to_connect.append(reg.registrant.chat_id)

                for hack_sponsor in hackathon.sponsors.all():
                    if not hack_sponsor.chat_channel_id:
                        created, channel_details = create_channel_if_not_exists({
                            'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                            'channel_display_name': f'company-{slugify(hack_sponsor.sponsor.name)}'[:60],
                            'channel_name': f'company-{hack_sponsor.sponsor.name}'[:60]
                        })
                        hack_sponsor.chat_channel_id = channel_details['id']
                        hack_sponsor.save()
                    channels_to_connect.append(hack_sponsor.chat_channel_id)

                for channel_id in channels_to_connect:
                    task = add_to_channel.s({'id': channel_id}, profiles_to_connect)
                    tasks.append(task)

            if len(tasks) > 0:
                job = group(tasks)
                result = job.apply_async()
            else:
                print("Nothing to Sync")

        except Exception as e:
            logger.error(str(e))
