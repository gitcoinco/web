'''
    Copyright (C) 2017 Gitcoin Core

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
import math
import warnings

from django.core.management.base import BaseCommand
from django.utils import timezone
from github.utils import get_emails_master
from dashboard.models import Tip
from dashboard.notifications import maybe_market_tip_to_email

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def assign_tip_to(tip, handle):
    tip.username = handle
    tip.emails = get_emails_master(to_username)
    maybe_market_tip_to_email(tip, tip.emails)
    return tip

class Command(BaseCommand):

    help = 'sends Tips automagically for anyone where is_for_bounty_fulfiller is True '

    def handle(self, *args, **options):
        tips = Tip.objects.filter(is_for_bounty_fulfiller=True, receive_txid='')
        for tip in tips:
            try:
                bounty = tip.bounty
                if bounty:
                    print(f" - tip {tip.pk} / {bounty.standard_bounties_id} / {bounty.status}")
                    if bounty.status == 'done':
                        fulfillment = bounty.fulfillments.filter(accepted=True).latest('fulfillment_id')
                        if fulfillment:
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
                        else:
                            ######################################################
                            # was sent with bulk payout.  send to bulk payout_ees
                            ######################################################
                            print(" - 2 ")
                            bpts = bounty.bulk_payout_tips
                            bpts_ids = bpts.values_list('pk', flat=True)
                            num_payees = bpts.count()

                            # TODO: make this number disproportionate, instead of equal parts
                            amount_to_pay = math.floor(tip.amount_in_wei / num_payees)
                            amount = math.floor(tip.amount / num_payees)

                            for bpt in bpts:
                                print(f"    - {bpt.pk} ")
                                cloned_tip = bpt
                                cloned_tip.pk = None  # effectively clones the bpt and inserts a new one
                                cloned_tip.receive_txid = ''
                                cloned_tip.amount = amount
                                cloned_tip.receive_address = ''
                                cloned_tip.recipient_profile = None
                                cloned_tip.is_for_bounty_fulfiller = False
                                cloned_tip.username = bpt.username
                                cloned_tip.emails = {}
                                cloned_tip.metadata['debug_info'] = f'created in order to facilitate payout of a crowdfund tip {tip.pk}'
                                tip = assign_tip_to(tip, cloned_tip.username)
                                cloned_tip.save()
                                tip = cloned_tip(tip, bounty.bounty_owner_address)

                            tip.receive_txid = f'cloned-and-paid-via-clones-:{bpts_ids}'
                            msg = f'auto assigneed on {timezone.now()} to via recipients of {bpts_ids}; as done ' \
                                  'bounty w no bountyfulfillment'
                            print("     ", msg)
                            tip.metadata['payout_comments'] = msg
                            tip.save()
                    elif bounty.status == 'cancelled':
                        ######################################################
                        # return to funder
                        ######################################################
                        print(" - 3 ")
                        # assign tip to fulfiller and email them
                        tip = assign_tip_to(tip, bounty.bounty_owner_address)
                        msg = f'auto assigneed on {timezone.now()}; as cancelled bounty'
                        print("     " + msg)
                        tip.metadata['payout_comments'] = msg
                        tip.save()
            except Exception as e:
                print(e)
                logger.exception(e)
