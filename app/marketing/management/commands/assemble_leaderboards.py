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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, Profile, Tip
from marketing.models import LeaderboardRank

IGNORE_PAYERS = []
IGNORE_EARNERS = ['owocki']  # sometimes owocki pays to himself. what a jerk!

days_back = 7
if settings.DEBUG:
    days_back = 30
weekly_cutoff = timezone.now() - timezone.timedelta(days=days_back)
monthly_cutoff = timezone.now() - timezone.timedelta(days=30)
quarterly_cutoff = timezone.now() - timezone.timedelta(days=90)
yearly_cutoff = timezone.now() - timezone.timedelta(days=365)


def default_ranks():
    return {
        'weekly_fulfilled': {},
        'weekly_all': {},
        'weekly_payers': {},
        'weekly_earners': {},
        'monthly_fulfilled': {},
        'monthly_all': {},
        'monthly_payers': {},
        'monthly_earners': {},
        'quarterly_fulfilled': {},
        'quarterly_all': {},
        'quarterly_payers': {},
        'quarterly_earners': {},
        'yearly_fulfilled': {},
        'yearly_all': {},
        'yearly_payers': {},
        'yearly_earners': {},
        'all_fulfilled': {},
        'all_all': {},
        'all_payers': {},
        'all_earners': {},
    }


ranks = default_ranks()


def add_element(key, username, amount):
    username = username.replace('@', '')
    if not username or username == "None":
        return
    if username not in ranks[key].keys():
        ranks[key][username] = 0
    ranks[key][username] += round(float(amount), 2)


def sum_bounties(b, usernames):
    for username in usernames:
        if b.idx_status == 'done':
            fulfiller_usernames = list(b.fulfillments.all().values_list('fulfiller_github_username', flat=True))
            add_element('all_fulfilled', username, b._val_usd_db)
            if username == b.bounty_owner_github_username and username not in IGNORE_PAYERS:
                add_element('all_payers', username, b._val_usd_db)
            if username in fulfiller_usernames and username not in IGNORE_EARNERS:
                add_element('all_earners', username, b._val_usd_db)
            if b.created_on > weekly_cutoff:
                add_element('weekly_fulfilled', username, b._val_usd_db)
                if username == b.bounty_owner_github_username and username not in IGNORE_PAYERS:
                    add_element('weekly_payers', username, b._val_usd_db)
                if username in fulfiller_usernames and username not in IGNORE_EARNERS:
                    add_element('weekly_earners', username, b._val_usd_db)
            if b.created_on > monthly_cutoff:
                add_element('monthly_fulfilled', username, b._val_usd_db)
                if username == b.bounty_owner_github_username and username not in IGNORE_PAYERS:
                    add_element('monthly_payers', username, b._val_usd_db)
                if username in fulfiller_usernames and username not in IGNORE_EARNERS:
                    add_element('monthly_earners', username, b._val_usd_db)
            if b.created_on > quarterly_cutoff:
                add_element('quarterly_fulfilled', username, b._val_usd_db)
                if username == b.bounty_owner_github_username and username not in IGNORE_PAYERS:
                    add_element('quarterly_payers', username, b._val_usd_db)
                if username in fulfiller_usernames and username not in IGNORE_EARNERS:
                    add_element('quarterly_earners', username, b._val_usd_db)
            if b.created_on > yearly_cutoff:
                add_element('yearly_fulfilled', username, b._val_usd_db)
                if username == b.bounty_owner_github_username and username not in IGNORE_PAYERS:
                    add_element('yearly_payers', username, b._val_usd_db)
                if username in fulfiller_usernames and username not in IGNORE_EARNERS:
                    add_element('yearly_earners', username, b._val_usd_db)

        add_element('all_all', username, b._val_usd_db)
        if b.created_on > weekly_cutoff:
            add_element('weekly_all', username, b._val_usd_db)
        if b.created_on > monthly_cutoff:
            add_element('monthly_all', username, b._val_usd_db)
        if b.created_on > yearly_cutoff:
            add_element('yearly_all', username, b._val_usd_db)


def sum_tips(t, usernames):
    val_usd = t.value_in_usdt_now
    for username in usernames:
        add_element('all_fulfilled', username, val_usd)
        add_element('all_earners', username, val_usd)
        if t.created_on > weekly_cutoff:
            add_element('weekly_fulfilled', username, val_usd)
            add_element('weekly_earners', username, val_usd)
            add_element('weekly_all', username, val_usd)
        if t.created_on > monthly_cutoff:
            add_element('monthly_fulfilled', username, val_usd)
            add_element('monthly_all', username, val_usd)
            add_element('monthly_earners', username, val_usd)
        if t.created_on > quarterly_cutoff:
            add_element('quarterly_fulfilled', username, val_usd)
            add_element('quarterly_all', username, val_usd)
            add_element('quarterly_earners', username, val_usd)
        if t.created_on > yearly_cutoff:
            add_element('yearly_fulfilled', username, val_usd)
            add_element('yearly_all', username, val_usd)
            add_element('yearly_earners', username, val_usd)


def should_suppress_leaderboard(handle):
    if not handle:
        return True
    profiles = Profile.objects.filter(handle__iexact=handle)
    if profiles.exists():
        profile = profiles.first()
        if profile.suppress_leaderboard:
            return True
        if profile.hide_profile:
            return True
    return False


class Command(BaseCommand):

    help = 'creates leaderboard objects'

    def handle(self, *args, **options):
        # get bounties
        bounties = Bounty.objects.current()

        # iterate
        for b in bounties:
            if not b._val_usd_db:
                continue

            usernames = []
            if not should_suppress_leaderboard(b.bounty_owner_github_username):
                usernames.append(b.bounty_owner_github_username)
            for fulfiller in b.fulfillments.all():
                if not should_suppress_leaderboard(fulfiller.fulfiller_github_username):
                    usernames.append(fulfiller.fulfiller_github_username)

            sum_bounties(b, usernames)

        # tips
        tips = Tip.objects.all()

        for t in tips:
            if not t.value_in_usdt_now:
                continue
            usernames = []
            if not should_suppress_leaderboard(t.username):
                usernames.append(t.username)

            sum_tips(t, usernames)

        # set old LR as inactive
        for lr in LeaderboardRank.objects.filter(active=True):
            lr.active = False
            lr.save()

        # save new LR in DB
        for key, rankings in ranks.items():
            for username, amount in rankings.items():
                LeaderboardRank.objects.create(
                    github_username=username,
                    leaderboard=key,
                    amount=amount,
                    active=True,
                    )
                print(key, username, amount)
