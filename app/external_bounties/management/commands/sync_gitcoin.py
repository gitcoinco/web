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

from dashboard.models import Bounty
from external_bounties.models import ExternalBounty


class Command(BaseCommand):

    help = 'syncs from other gitcoin'

    def handle(self, *args, **options):

        bounties = Bounty.objects.filter(current_bounty=True, network='mainnet', idx_status__in=['open', 'started', 'submitted'])
        for bounty in bounties:
            if False:
                continue
            try:
                denomination = bounty.token_name
                amount = bounty.value_true
                payout_str = str(round(amount, 2)) + " " + denomination
                tags = ['Gitcoin']
                try:
                    tags = tags + bounty.keywords.split(',')
                except:
                    pass
                ExternalBounty.objects.get_or_create(
                        action_url=bounty.url,
                        active=True,
                        description=bounty.issue_description,
                        source_project='Gitcoin',
                        amount=amount,
                        amount_denomination=denomination,
                        tags=tags,
                        title=bounty.title,
                        payout_str=payout_str,
                    )
                print("HERE")
            except Exception as e:
                print(e)
