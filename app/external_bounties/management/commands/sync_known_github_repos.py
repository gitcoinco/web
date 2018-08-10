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

from external_bounties.models import ExternalBounty
from git.utils import get_issues


class Command(BaseCommand):

    help = 'syncs from other bounty provider'

    def handle(self, *args, **options):

        known_repos = [
            ('JGcarv', 'ethereum-bounty-hunters')
        ]

        for owner, repo in known_repos:
            issues = get_issues(owner, repo)
            for bounty in issues:
                payout_str = ''
                try:
                    ExternalBounty.objects.get_or_create(
                        action_url=bounty['url'],
                        active=True,
                        description=bounty['body'],
                        source_project=repo,
                        amount=None,
                        amount_denomination='',
                        tags=[repo],
                        title=bounty['title'],
                        payout_str=payout_str,
                    )
                except Exception as e:
                    print(e)
