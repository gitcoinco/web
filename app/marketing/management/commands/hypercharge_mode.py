# -*- coding: utf-8 -*-
"""Define the GDPR reconsent command for EU users.

Copyright (C) 2021 Gitcoin Core

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
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.template.defaultfilters import floatformat
from django.utils import timezone

from dashboard.models import Bounty, BountyEvent, Profile
from marketing.mails import bounty_hypercharged
from townsquare.models import Offer


def make_secret_offer(profile, title, desc, bounty):
    utm = f'utm_source=hypercharge-auto-secret&utm_medium=gitcoinbot&utm_campaign={bounty.title}'
    Offer.objects.create(
        created_by=profile,
        title=title,
        desc=desc,
        key='secret',
        url=f'{bounty.absolute_url}?{utm}',
        valid_from=timezone.now(),
        valid_to=timezone.now() + timezone.timedelta(hours=3),
        public=True,
        style=f'back{random.randint(0, 32)}',
        from_name=bounty.org_display_name
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
        now = timezone.now()
        profile = Profile.objects.filter(handle='gitcoinbot').first()

        bounties = Bounty.objects.current().filter(hypercharge_mode=True, hyper_next_publication__lt=now)
        bounties = bounties.exclude(bounty_state__in=['done', 'cancelled'])
        bounties = bounties.order_by('metadata__hyper_tweet_counter')


        if bounties:
            bounty = bounties.first()

            offer_title = f'Work on "{bounty.title}" and receive {floatformat(bounty.value_true)} {bounty.token_name}'
            offer_desc = ''

            counter = bounty.metadata['hyper_tweet_counter']
            # counter is 0 -> new_bounty
            # counter is 1 -> remarket_bounty
            if counter == 0:
                notify_previous_workers(bounty)
                make_secret_offer(profile, offer_title, offer_desc, bounty)
            elif counter % 2 == 0:
                make_secret_offer(profile, offer_title, offer_desc, bounty)

            bounty.metadata['hyper_tweet_counter'] += 1
            bounty.hyper_next_publication = now + timedelta(hours=12)
            bounty.save()
