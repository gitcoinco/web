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

import requests
from external_bounties.models import ExternalBounty


class Command(BaseCommand):

    help = 'syncs from other bounty provider'

    def handle(self, *args, **options):

        url = 'https://api.bounty0x.io/v1/bounty/'

        headers = {
            'origin': 'https://alpha.bounty0x.io',
            'clientidentifier': 'Kzn9ureLQmDrx7AT3Kcd',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
            'accept-language': 'en-US,en;q=0.9',
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://alpha.bounty0x.io/bounties',
            'authority': 'api.bounty0x.io',
            'dnt': '1',
        }

        response = requests.get(url, headers=headers)
        bounties = response.json()
        for bounty in bounties:
            if False:
                continue
            try:
                url = 'https://alpha.bounty0x.io/bounties/{}'.format(bounty['bountyID'])
                amount = None
                denomination = ''
                payout_str = ''
                try:
                    amount, denomination = bounty['payout'].replace(',','').split(' ')
                    amount = int(amount)
                except:
                    payout_str = bounty['payout']
                    if not payout_str:
                        payout_str=''
                    amount = None
                ExternalBounty.objects.get_or_create(
                        action_url=url,
                        active=True,
                        description=bounty['description'],
                        source_project='Bounty0x',
                        amount=amount,
                        amount_denomination=denomination,
                        tags=['Bounty0x'],
                        title=bounty['title'],
                        payout_str=payout_str,
                    )
                print("HERE")
            except Exception as e:
                print(e)
