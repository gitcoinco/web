# -*- coding: utf-8 -*-
"""Define the GDPR reconsent command for EU users.

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

"""
import operator
import random
import time
import warnings
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Activity, Earning, Profile, Bounty, Interest, BountyEvent
from dashboard.notifications import maybe_market_to_twitter
from economy.utils import convert_token_to_usdt
from grants.models import *
from grants.models import CartActivity, Contribution, PhantomFunding
from grants.views import clr_round, next_round_start, round_end
from marketing.mails import bounty_hypercharged
from townsquare.models import Comment, Offer


def make_secret_offer(profile, title, desc, bounty):
    Offer.objects.create(
        created_by=profile,
        title=title,
        desc=desc,
        key='secret',
        url=bounty.absolute_url,
        valid_from=timezone.now(),
        valid_to=timezone.now() + timezone.timedelta(days=1),
        public=True,
    )

def notify_previous_workers(bounty):
    emails = set()
    prev_bounties = Bounty.objects.filter(bounty_owner_profile=bounty.bounty_owner_profile).values_list('id', flat=True)
    if bounty.bounty_owner_profile.is_org:
        previous_works = BountyEvent.objects.filter(event_type='submit_work', bounty__in=prev_bounties)
        for work in previous_works:
            emails.add(work.created_by.email)

    bounty_hypercharged(bounty, list(emails))


class Command(BaseCommand):
    help = 'post hyper bounties to twitter'

    def handle(self, *args, **options):
        offer_title = ''
        offer_desc = ''
        now = timezone.now()
        profile = Profile.objects.filter(handle='gitcoinbot').first()

        bounties = Bounty.objects.current().filter(
            network='mainnet', idx_status='open',
            expires_date__gt=now, hyper_next_publication__lt=now).order_by('metadata__hyper_tweet_counter')
        bounty = bounties.first()

        if bounty:
            event_name = ''
            counter = bounty.metadata['hyper_tweet_counter']
            if counter == 0:
                event_name = 'new_bounty'
                notify_previous_workers(bounty.bounty_owner_profile)
                make_secret_offer(profile, offer_title, offer_desc, bounty)
            elif counter == 1:
                event_name = 'remarket_bounty'
            elif counter % 2 == 0:
                make_secret_offer(profile, offer_title, offer_desc, bounty)

            bounty.bounty.metadata['hyper_tweet_counter'] += 1
            bounty.hyper_next_publication = now + timedelta(hours=12)
            bounty.save()

            maybe_market_to_twitter(bounty, event_name)
