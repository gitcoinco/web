'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from dashboard.models import Bounty
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'refreshes the triggers associated with current bounties'

    def handle(self, *args, **options):

        current_bounties = Bounty.objects.filter(current_bounty=True).all()
        for b in current_bounties:
            b.save()
            print('1/ refreshed {}'.format(b.pk))

        all_bounties = Bounty.objects.all()
        for b in all_bounties:
            if not b.avatar_url:
                b.avatar_url = b.get_avatar_url()
            b.save()
            print('2/ refreshed {}'.format(b.pk))
