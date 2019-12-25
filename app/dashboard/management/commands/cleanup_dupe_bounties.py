'''
    Copyright (C) 2019 Gitcoin Core

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

from dashboard.helpers import merge_bounty
from dashboard.models import Bounty


class Command(BaseCommand):

    help = 'cleans up duplicate bounties'

    def handle(self, *args, **options):
        
        handled_bounties = []
        for bounty in Bounty.objects.filter(current_bounty=True).order_by('-pk'):

            if bounty.pk not in handled_bounties:

                # mark bounty as handled
                handled_bounties.append(bounty.pk)
                evil_twins = Bounty.objects.exclude(pk=bounty.pk).filter(current_bounty=True, github_url=bounty.github_url, network=bounty.network, standard_bounties_id=bounty.standard_bounties_id)
                for evil_twin in evil_twins:
                    print(f"dupe @ ({bounty.github_url}, {bounty.network}, {bounty.standard_bounties_id})..")
                    print(f"-merging  {evil_twin.pk}, into {bounty.pk}")

                    handled_bounties.append(evil_twin.pk)
                    merge_bounty(evil_twin, bounty, {}, {}, verbose=False)
