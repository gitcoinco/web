# -*- coding: utf-8 -*-
"""Define the Grant utilities.

Copyright (C) 2020 Gitcoin Core

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
import os
from secrets import token_hex

from perftools.models import JSONStore


def get_upload_filename(instance, filename):
    salt = token_hex(16)
    file_path = os.path.basename(filename)
    return f"grants/{getattr(instance, '_path', '')}/{salt}/{file_path}"


def get_leaderboard():
    return JSONStore.objects.filter(view='grants', key='leaderboard').order_by('-pk').first().data


def generate_leaderboard(max_items=100):
    from grants.models import Subscription, Contribution
    handles = Subscription.objects.all().values_list('contributor_profile__handle', flat=True)
    default_dict = {
        'rank': None,
        'no': 0,
        'sum': 0,
        'handle': None,
    }
    users_to_results = { ele : default_dict.copy() for ele in handles }

    # get all contribution attributes
    for contribution in Contribution.objects.all().select_related('subscription'):
        key = contribution.subscription.contributor_profile.handle
        users_to_results[key]['handle'] = key
        amount = contribution.subscription.get_converted_amount()
        if amount:
            users_to_results[key]['no'] += 1
            users_to_results[key]['sum'] += round(amount)
    # prepare response for view
    items = []
    counter = 1
    for item in sorted(users_to_results.items(), key=lambda kv: kv[1]['sum'], reverse=True):
        item = item[1]
        if item['no']:
            item['rank'] = counter
            items.append(item)
            counter += 1
    return items[:max_items]


def is_grant_team_member(grant, profile):
    """Checks to see if profile is a grant team member

    Args:
        grant (grants.models.Grant): The grant in question.
        profile (dashboard.models.Profile): The current user's profile.

    """
    is_team_member = False
    if grant.admin_profile == profile:
        is_team_member = True
    else:
        for team_member in grant.team_members.all():
            if team_member.id == profile.id:
                is_team_member = True
                break
    return is_team_member
