# -*- coding: utf-8 -*-
"""Handle dashboard related signals.

Copyright (C) 2021 Gitcoin Core

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
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from corsheaders.signals import check_request_enabled
from git.utils import get_gh_issue_details, get_url_dict, issue_number, org_name, repo_name

from .notifications import maybe_market_to_github

logger = logging.getLogger(__name__)


def m2m_changed_interested(sender, instance, action, reverse, model, **kwargs):
    """Handle changes to Bounty interests."""

    if action in ['post_add', 'post_remove']:
        from dashboard.tasks import m2m_changed_interested
        m2m_changed_interested.delay(instance.pk)



def changed_fulfillments(sender, instance, action, reverse, model, **kwargs):
    """Handle changes to Bounty fulfillments."""
    event_name = 'work_submitted'
    profile_handles = []

    fulfillments = instance.fulfillments.select_related('profile').all().order_by('pk')
    if fulfillments.filter(accepted=True).exists():
        event_name = 'work_done'

    for fulfillment in fulfillments:
        profile_handles.append((fulfillment.profile.handle, fulfillment.profile.absolute_url))

    if action in ['post_add', 'post_remove']:
        maybe_market_to_github(instance, event_name, profile_pairs=profile_handles)


def allow_all_bounties(sender, request, **kwargs):
    return request.method == 'GET' and request.path.startswith('/api/v0.1/bounties/')


check_request_enabled.connect(allow_all_bounties)
