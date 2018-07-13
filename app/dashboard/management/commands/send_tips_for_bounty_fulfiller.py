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

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Tip


class Command(BaseCommand):

    help = 'sends Tips automagically for anyone where is_for_bounty_fulfiller is True '

    def handle(self, *args, **options):
        tips = Tip.objects.filter(is_for_bounty_fulfiller=True, receive_txid='')
        for tip in tips:
            bounty = tip.bounty
            if bounty:
                print(f"{tip.pk} / {bounty.pk} / {bounty.status}")
                if bounty.status == 'done':
                    fulfillment = new_bounty.fulfillments.filter(accepted=True).latest('fulfillment_id')
                    if fulfillment:
                        # send to fulfiller
                        # TODO
                        pass
                    else:
                        # was sent with bulk payout.  send to bulk payout_ees
                        # TODO
                        pass

                if bounty.status == 'cancelled':
                    # return to user
                    pass
