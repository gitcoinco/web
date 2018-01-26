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

from dashboard.helpers import normalizeURL
from dashboard.models import Bounty, BountySyncRequest
from dashboard.notifications import (
    maybe_market_to_email, maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter,
)


def process_bounty_details(bountydetails, url, contract_address, network):
    """Process legacy bounty details."""
    url = normalizeURL(url)

    #extract json
    metadata = None
    claimee_metadata = None
    try:
        metadata = json.loads(bountydetails[8])
    except Exception as e:
        print(e)
        metadata = {}
    try:
        claimee_metadata = json.loads(bountydetails[10])
    except Exception as e:
        print(e)
        claimee_metadata = {}

    #create new bounty (but only if things have changed)
    didChange = False
    old_bounties = Bounty.objects.none()
    try:
        old_bounties = Bounty.objects.filter(
            github_url=url,
            title=metadata.get('issueTitle'),
            current_bounty=True,
        ).order_by('-created_on')
        didChange = (bountydetails != old_bounties.first().raw_data)
        if not didChange:
            return (didChange, old_bounties.first(), old_bounties.first())
    except Exception as e:
        print(e)
        didChange = True

    with transaction.atomic():
        for old_bounty in old_bounties:
            old_bounty.current_bounty = False
            old_bounty.save()
        new_bounty = Bounty.objects.create(
            title=metadata.get('issueTitle',''),
            web3_created=timezone.datetime.fromtimestamp(bountydetails[7]),
            value_in_token=bountydetails[0],
            token_name=metadata.get('tokenName'),
            token_address=bountydetails[1],
            bounty_type=metadata.get('bountyType'),
            project_length=metadata.get('projectLength'),
            experience_level=metadata.get('experienceLevel'),
            github_url=url,
            bounty_owner_address=bountydetails[2],
            bounty_owner_email=metadata.get('notificationEmail', None),
            bounty_owner_github_username=metadata.get('githubUsername', None),
            claimeee_address=bountydetails[3],
            claimee_email=claimee_metadata.get('notificationEmail', None),
            claimee_github_username=claimee_metadata.get('githubUsername', None),
            is_open=bountydetails[4],
            expires_date=timezone.datetime.fromtimestamp(bountydetails[9]),
            raw_data=bountydetails,
            metadata=metadata,
            claimee_metadata=claimee_metadata,
            current_bounty=True,
            contract_address=contract_address,
            network=network,
            issue_description='',
            )
        if not new_bounty.avatar_url:
            new_bounty.avatar_url = new_bounty.get_avatar_url()
        new_bounty.save()

    return (didChange, old_bounties.first(), new_bounty)


def process_bounty_changes(old_bounty, new_bounty, txid):
    """Process legacy bounty changes."""
    # process bounty sync requests
    did_bsr = False
    for bsr in BountySyncRequest.objects.filter(processed=False, github_url=new_bounty.github_url):
        did_bsr = True
        bsr.processed = True
        bsr.save()

    # new bounty
    null_address = '0x0000000000000000000000000000000000000000'
    if (old_bounty is None and new_bounty and new_bounty.is_open) or (not old_bounty.is_open and new_bounty.is_open):
        event_name = 'new_bounty'
    elif old_bounty.claimeee_address == null_address and new_bounty.claimeee_address != null_address:
        event_name = 'new_claim'
    elif old_bounty.is_open and not new_bounty.is_open:
        event_name = 'approved_claim'
    elif old_bounty.claimeee_address != null_address and new_bounty.claimeee_address == null_address:
        event_name = 'rejected_claim'
    else:
        event_name = 'unknown_event'
    print(event_name)

    # marketing
    print("============ posting ==============")
    did_post_to_twitter = maybe_market_to_twitter(new_bounty, event_name, txid)
    did_post_to_slack = maybe_market_to_slack(new_bounty, event_name, txid)
    did_post_to_github = maybe_market_to_github(new_bounty, event_name, txid)
    did_post_to_email = maybe_market_to_email(new_bounty, event_name, txid)
    print("============ done posting ==============")

    # what happened
    what_happened = {
        'did_bsr': did_bsr,
        'did_post_to_email': did_post_to_email,
        'did_post_to_github': did_post_to_github,
        'did_post_to_slack': did_post_to_slack,
        'did_post_to_twitter': did_post_to_twitter,
    }

    print("changes processed: ")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(what_happened)
