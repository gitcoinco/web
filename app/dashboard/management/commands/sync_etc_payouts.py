'''
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

'''


from django.core.management.base import BaseCommand

from dashboard.models import Bounty

class Command(BaseCommand):

    help = 'checks if payments are confirmed for ETC bounties that have been paid out'

    def handle(self, *args, **options):
        bounties_to_check = Bounties.objects.filter(
            payout_tx_id=None, bounty_state='done', token_name='ETC',
            network='ETC')
        for bounty in bounties_to_check.all():
            t = search_for_etc_bounty_payout(bounty)
            if t:
                if not etc_txn_already_used(t):
                    bounty.payout_tx_id = t['hash']
                    bounty.save()
                    if get_etc_txn_status.get('has_mined'):
                        bounty.payout_confirmed = True
                        bounty.save()
