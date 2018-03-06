# -*- coding: utf-8 -*-
"""Handle legacy helpers.

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

import json
import pprint

from django.db import transaction
from django.utils import timezone

from dashboard.helpers import normalize_url
from dashboard.models import Bounty, BountySyncRequest
from dashboard.notifications import (
    maybe_market_to_email, maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter,
)
from dashboard.utils import build_profile_pairs


def process_bounty_details(bountydetails, url, contract_address, network):
    """Process legacy bounty details."""
    url = normalize_url(url)

    # extract json
    metadata = None
    try:
        metadata = json.loads(bountydetails[8])
    except Exception as e:
        print(e)
        metadata = {}

    # create new bounty (but only if things have changed)
    did_change = False
    old_bounties = Bounty.objects.none()
    try:
        old_bounties = Bounty.objects.current().filter(
            github_url=url,
            title=metadata.get('issueTitle'),
        ).order_by('-created_on')
        did_change = (bountydetails != old_bounties.first().raw_data)
        if not did_change:
            return (did_change, old_bounties.first(), old_bounties.first())
    except Exception as e:
        print(e)
        did_change = True

    with transaction.atomic():
        new_bounty = Bounty.objects.create(
            title=metadata.get('issueTitle', ''),
            web3_type='legacy_gitcoin',
            web3_created=timezone.datetime.fromtimestamp(bountydetails[7]),
            value_in_token=bountydetails[0],
            token_name=metadata.get('tokenName'),
            token_address=bountydetails[1],
            bounty_type=metadata.get('bountyType'),
            project_length=metadata.get('projectLength'),
            experience_level=metadata.get('experienceLevel'),
            github_url=url,
            bounty_owner_address=bountydetails[2],
            bounty_owner_email=metadata.get('notificationEmail', ''),
            bounty_owner_github_username=metadata.get('githubUsername', ''),
            is_open=bountydetails[4],
            expires_date=timezone.datetime.fromtimestamp(bountydetails[9]),
            raw_data=bountydetails,
            metadata=metadata,
            current_bounty=True,
            contract_address=contract_address,
            network=network,
            issue_description='',
        )
        for old_bounty in old_bounties:
            if old_bounty.current_bounty:
                old_num_fulfillments = old_bounty.fulfillments.count()
                old_bounty.num_fulfillments = old_num_fulfillments
                old_bounty.fulfillments.update(bounty=new_bounty)
                if new_bounty.num_fulfillments < old_num_fulfillments or \
                   new_bounty.num_fulfillments < new_bounty.fulfillments.count():
                    new_bounty.num_fulfillments = new_bounty.fulfillments.count()
                    new_bounty.save()
            old_bounty.current_bounty = False
            old_bounty.save()
        new_bounty.fetch_issue_item()
        if not new_bounty.avatar_url:
            new_bounty.avatar_url = new_bounty.get_avatar_url()
        new_bounty.save()

    return (did_change, old_bounties.first(), new_bounty)


def process_bounty_changes(old_bounty, new_bounty):
    """Process legacy bounty changes.

    Args:
        old_bounty (dashboard.models.Bounty): The old Bounty object.
        new_bounty (dashboard.models.Bounty): The new Bounty object.

    """
    # process bounty sync requests
    did_bsr = False
    for bsr in BountySyncRequest.objects.filter(processed=False, github_url=new_bounty.github_url):
        did_bsr = True
        bsr.processed = True
        bsr.save()

    # new bounty
    if (not old_bounty and new_bounty and new_bounty.is_open) or (not old_bounty.is_open and new_bounty.is_open):
        event_name = 'new_bounty'
    elif old_bounty.num_fulfillments < new_bounty.num_fulfillments:
        event_name = 'work_submitted'
    elif old_bounty.is_open and not new_bounty.is_open:
        if new_bounty.status == 'cancelled':
            event_name = 'killed_bounty'
        else:
            event_name = 'work_done'
    else:
        event_name = 'unknown_event'
    print(event_name)

    # Build profile pairs list
    if new_bounty.fulfillments.exists():
        profile_pairs = build_profile_pairs(new_bounty)

    # marketing
    if event_name != 'unknown_event':
        print("============ posting ==============")
        did_post_to_twitter = maybe_market_to_twitter(new_bounty, event_name)
        did_post_to_slack = maybe_market_to_slack(new_bounty, event_name)
        did_post_to_github = maybe_market_to_github(new_bounty, event_name, profile_pairs)
        did_post_to_email = maybe_market_to_email(new_bounty, event_name)
        print("============ done posting ==============")

        # what happened
        what_happened = {
            'did_bsr': did_bsr,
            'did_post_to_email': did_post_to_email,
            'did_post_to_github': did_post_to_github,
            'did_post_to_slack': did_post_to_slack,
            'did_post_to_twitter': did_post_to_twitter,
        }

        print("Legacy changes processed: ")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(what_happened)
    else:
        print('No notifications sent - Legacy Event Type Unknown = did_bsr: ', did_bsr)
