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
from chat.tasks import hackathon_chat_sync
from chat.tasks import create_channel_if_not_exists, associate_chat_to_profile
from dashboard.models import HackathonEvent, HackathonRegistration, Interest, Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sync Active Hackathons"

    def handle(self, *args, **options):
        try:

            today = datetime.now()
            hackathons_to_sync = HackathonEvent.objects.filter(
                start_date__gte=today,
                end_date__lte=today
            )

            for hackathon in hackathons_to_sync:
                try:
                    hackathon_chat_sync.delay(hackathon.id)
                    logger.info(f'Queued Hackathon Chat Sync Job for ID: {hackathon.id}')
                except Exception as e:
                    logger.error(str(e))
                    continue

        except Exception as e:
            logger.error(str(e))
