# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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


def return_to_sender(tip, msg, comments_public):
    old_from = tip.from_name
    tip.from_name = 'gitcoinbot'
    tip.metadata['payout_comments'] = msg
    print("     " + msg)
    tip.comments_public = comments_public
    tip.save()
    tip = assign_tip_to(tip, old_from)
    tip.save()


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
                    if bounty.status == 'done':
                        fulfillment = bounty.fulfillments.filter(accepted=True)
                        if fulfillment.exists():
                            fulfillment = fulfillment.latest('fulfillment_id')
                            ######################################################
                            # send to fulfiller
                            ######################################################
                            print(" - 1 ")
                            # assign tip to fulfiller and email them
                            msg = f'auto assigneed on {timezone.now()} to fulfillment {fulfillment.pk}; as done bountyfulfillment'
                            print("     " + msg)
                            tip.metadata['payout_comments'] = msg
                            tip.save()
                            tip = assign_tip_to(tip, fulfillment.fulfiller_github_username)
                            tip.save()
                        else:
                            ######################################################
                            # was sent with bulk payout.  return to sender
                            ######################################################
                            print(" - 2 ")
                            old_from = tip.from_name
                            comments_public = "[gitcoinbot message] This crowdfunding was auto-returned to you because Gitcoin could not figure out how to distribute the funds.  We recommend that you payout these funds to the bounty hunters, at your discretion, via https://gitcoin.co/tip ."
                            msg = f'auto assigneed on {timezone.now()}; as bulk payout bounty.  tip was from {tip.from_name}'
                            return_to_sender(tip, msg, comments_public)
                    elif bounty.status == 'cancelled':
                        ######################################################
                        # return to funder
                        ######################################################
                        print(" - 3 ")
                        # assign tip to fulfiller and email them
                        old_from = tip.from_name
                        comments_public = "[gitcoinbot message] This funding was auto-returned to you because the bounty it was associated with was cancelled."
                        msg = f'auto assigneed on {timezone.now()}; as cancelled bounty.  tip was from {tip.from_name}'
                        return_to_sender(tip, msg, comments_public)
            except Exception as e:
                print(e)
                logger.exception(e)
