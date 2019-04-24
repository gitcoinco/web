# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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

import logging
import warnings

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Tip
from dashboard.notifications import maybe_market_tip_to_email
from git.utils import get_emails_master

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def assign_tip_to(tip, handle):
    tip.username = handle
    tip.emails = get_emails_master(handle)
    maybe_market_tip_to_email(tip, tip.emails)
    tip.metadata['is_for_bounty_fulfiller_handled'] = True
    return tip

class Command(BaseCommand):

    help = 'sends Tips automagically for anyone where is_for_bounty_fulfiller is True '

    def handle(self, *args, **options):
        tips = Tip.objects.filter(
            is_for_bounty_fulfiller=True,
            receive_txid='',
            metadata__is_for_bounty_fulfiller_handled__isnull=True
            ).send_success()
        for tip in tips:
            try:
                bounty = tip.bounty
                if bounty:
                    print(f" - tip {tip.pk} / {bounty.standard_bounties_id} / {bounty.status}")
                    fulfillment = bounty.fulfillments.filter(accepted=True)
                    send_to_fulfilled_parties = bounty.status == 'done' and fulfillment.exists()
                    send_back_to_where_it_came = bounty.status == 'cancelled' or (bounty.status == 'done' and not fulfillment.exists())
                    if send_to_fulfilled_parties:
                        fulfillment = fulfillment.latest('fulfillment_id')
                        ######################################################
                        # send to fulfiller
                        ######################################################
                        print(" - 1 ")
                        # assign tip to fulfiller and email them
                        tip = assign_tip_to(tip, fulfillment.fulfiller_github_username)
                        msg = f'auto assigneed on {timezone.now()} to fulfillment {fulfillment.pk}; as done bountyfulfillment'
                        print("     " + msg)
                        tip.metadata['payout_comments'] = msg
                        tip.save()
                    elif send_back_to_where_it_came:
                        ######################################################
                        # return to funder
                        ######################################################
                        print(" - 3 ")
                        # assign tip to fulfiller and email them
                        old_from = tip.from_name
                        tip.from_name = 'gitcoinbot'
                        tip = assign_tip_to(tip, old_from)
                        msg = f'auto assigneed on {timezone.now()}; as cancelled bounty.  tip was from {tip.from_name}'
                        tip.metadata['payout_comments'] = msg
                        print("     " + msg)
                        tip.comments_public = "[bot message] This funding was auto-returned to you because the bounty it was associated with was cancelled."
                        tip.save()
            except Exception as e:
                print(e)
                logger.exception(e)
