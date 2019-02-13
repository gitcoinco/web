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

from dashboard.models import Bounty


class Command(BaseCommand):

    help = 'cleans up activity feed items that have become detached from their current_bounty'

    def handle(self, *args, **options):

        for bounty in Bounty.objects.filter(current_bounty=False).order_by('-pk'):
            if bounty.activities.count():
                print(bounty.pk, bounty.activities.count())
            for activity in bounty.activities.all():
                activity.bounty = Bounty.objects.filter(standard_bounties_id=bounty.standard_bounties_id, network=bounty.network, current_bounty=True).order_by('-pk').first()
                activity.save()
