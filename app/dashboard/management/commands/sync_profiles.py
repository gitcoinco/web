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

from app.utils import sync_profile
from dashboard.models import Bounty, Profile
from dashboard.utils import is_blocked
from marketing.utils import is_deleted_account


def does_need_refresh(handle):
    needs_refresh = False
    org = None
    try:
        org = Profile.objects.get(handle=handle)
        org.last_sync_date > timezone.now() - timezone.timedelta(weeks=1)
    except Exception:
        needs_refresh = True

    return needs_refresh


class Command(BaseCommand):

    help = 'syncs orgs with github'

    def add_arguments(self, parser):
        parser.add_argument(
            '-force', '--force',
            action='store_true',
            dest='force_refresh',
            default=False,
            help='Force the refresh'
        )

    def handle(self, *args, **options):
        # setup
        handles = set([b.org_name for b in Bounty.objects.current()])
        for handle in handles:
            handle = handle.lower()
            print(handle)
            if is_blocked(handle)or is_deleted_account(handle):
                print('not syncing, handle is blocked')
                continue

            # does this handle need a refresh
            needs_refresh = does_need_refresh(handle) or options['force_refresh']

            if not needs_refresh:
                print('- no refresh needed')
            else:
                try:
                    sync_profile(handle)
                except Exception as e:
                    print(e)

            if not settings.DEBUG:
                time.sleep(60)
