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
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from dashboard.models import Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "create users to Gitcoin chat, creates the user if it doesn't exist"

    def add_arguments(self, parser):
        parser.add_argument('--days_ago', default=30, type=int)

    def handle(self, *args, **options):
        try:
            from chat.tasks import associate_chat_to_profile

            days_ago = options['days_ago']

            now = timezone.now()
            delta = timedelta(days=days_ago)

            profiles = Profile.objects.filter(
                Q(gitcoin_chat_access_token__exact='') | Q(chat_id__exact=''),
                last_visit__gte=now - delta,
                user__is_active=True
            ).prefetch_related('user')

            for profile in profiles:
                try:
                    logger.info(f'Syncing Gitcoin Chat Data for: {profile.handle} Started')
                    created, profile = associate_chat_to_profile(profile)
                    logger.info(f'Syncing Gitcoin Chat Data for: {profile.handle} Complete')
                except Exception as e:
                    logger.info(f'Failed to associate chat to profile for: {profile.handle}')
                    logger.info(str(e))

        except ConnectionError as exec:
            logger.info(str(exec))
            self.retry(countdown=30)
        except Exception as e:
            logger.info(str(e))
