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
from dashboard.models import Bounty
from marketing.models import LeaderboardRank
from django.conf import settings

days_back = 7
if settings.DEBUG:
    days_back = 30
weekly_cutoff = timezone.now() - timezone.timedelta(days=days_back)
monthly_cutoff = timezone.now() - timezone.timedelta(days=30)
yearly_cutoff = timezone.now() - timezone.timedelta(days=365)

ranks = {
    'weekly_fulfilled': {},
    'weekly_all': {},
    'monthly_fulfilled': {},
    'monthly_all': {},
    'yearly_fulfilled': {},
    'yearly_all': {},
    'all_fulfilled': {},
    'all_all': {},
}

def add_element(key, username, amount):
    username = username.replace('@', '')
    if username not in ranks[key].keys():
        ranks[key][username] = 0
    ranks[key][username] += amount

def sum_bounties(b, usernames):
    for username in usernames:
        
        if b.idx_status == 'fulfilled':
            add_element('all_fulfilled', username, b._val_usd_db)
            if b.created_on > weekly_cutoff:
                add_element('weekly_fulfilled', username, b._val_usd_db)
            if b.created_on > monthly_cutoff:
                add_element('monthly_fulfilled', username, b._val_usd_db)
            if b.created_on > yearly_cutoff:
                add_element('yearly_fulfilled', username, b._val_usd_db)

        add_element('all_all', username, b._val_usd_db)
        if b.created_on > weekly_cutoff:
            add_element('weekly_all', username, b._val_usd_db)
        if b.created_on > monthly_cutoff:
            add_element('monthly_all', username, b._val_usd_db)
        if b.created_on > yearly_cutoff:
            add_element('yearly_all', username, b._val_usd_db)

class Command(BaseCommand):

    help = 'creates leaderboard objects'

    def handle(self, *args, **options):


        bounties = Bounty.objects.filter(
            current_bounty=True,
            created_on__gt=weekly_cutoff,
            )

        for b in bounties:
            if not b._val_usd_db:
                continue

            usernames = []
            if b.bounty_owner_github_username:
                usernames.append(b.bounty_owner_github_username)
            if b.claimee_github_username:
                usernames.append(b.claimee_github_username)

            sum_bounties(b, usernames)

        for lr in LeaderboardRank.objects.filter(active=True):
            lr.active = False
            lr.save()

        for key, rankings in ranks.items():
            for username, amount in rankings.items():
                LeaderboardRank.objects.create(
                    github_username=username,
                    leaderboard=key,
                    amount=amount,
                    active=True,
                    )
                print(key, username, amount)



