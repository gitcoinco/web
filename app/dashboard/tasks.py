# -*- coding: utf-8 -*-
"""Define the Dashboard specific tasks.

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

"""
import time

from django.conf import settings
from django.utils import timezone

from app.celery import app
from app.utils import sync_profile

from .models import Bounty, Profile


def does_need_refresh(handle):
    """Determine whether or not a refresh is necessary.

    Args:
        handle (str): The profile handle to be synced.

    Returns:
        bool: Whether or not the Profile needs to be refreshed.

    """
    needs_refresh = False
    org = None
    try:
        org = Profile.objects.get(handle=handle)
        org.last_sync_date > timezone.now() - timezone.timedelta(weeks=1)
    except Exception:
        needs_refresh = True

    return needs_refresh


@app.task
def sync_profile_data(force_refresh=False, iteration_sleep=False):
    """Sync all handle data of current bounties."""
    handles = set([b.org_name for b in Bounty.objects.filter(current_bounty=True)])
    for handle in handles:
        print(handle)

        # does this handle need a refresh
        needs_refresh = does_need_refresh(handle) or force_refresh

        if not needs_refresh:
            print('- no refresh needed')
        else:
            try:
                sync_profile(handle)
            except Exception as e:
                print(e)

        if not settings.DEBUG and iteration_sleep:
            time.sleep(60)
