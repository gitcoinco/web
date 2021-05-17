# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import F, Max
from django.utils import timezone

from dashboard.utils import get_tx_status, has_tx_mined
from grants.models import CartActivity, Contribution, Grant, Subscription
from grants.views import next_round_start, round_end  # TODO-SELF-SERVICE: REMOVE THIS
from marketing.mails import remember_your_cart, warn_subscription_failed
from townsquare.models import MatchRound


class Command(BaseCommand):
    help = 'Sent reminder to user who forgot its cart '

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            default=False,
            type=bool,
            help="Only process and display the carts to being delivered"
        )
        parser.add_argument(
            '--full-cart',
            default=False,
            type=bool,
            help="Should the cart being delivered partially"
        )
        parser.add_argument(
            '--hours',
            type=int,
            help="how many hours forward to full to look"
        )


    def handle(self, *args, **options):
        last_activity_by_user = CartActivity.objects.filter(latest=True, created_on__gt=next_round_start).exclude(metadata=[])
        count = 0
        if options.get('hours'):
            hours = options.get('hours')
        else:
            hours = int((round_end - datetime.now()).total_seconds() / 3600)

        for activity in last_activity_by_user:
            print(activity)

            # Check if this cart is still valid
            no_checkout_grants = []
            for grant_entry in activity.metadata:
                subscription = Subscription.objects.filter(grant_id=grant_entry['grant_id'],
                                                           contributor_profile=activity.profile,
                                                           created_on__gt=activity.created_on,
                                                           created_on__lte=round_end).first()

                if not subscription:
                    no_checkout_grants.append(grant_entry)

            if options['full_cart']:
                if len(no_checkout_grants) != len(activity.metadata):
                    print(f' * Activity {activity.id}: The grants were partially contributed but no notification will be delivered')
                    continue

            cart_query = [f'{grant["grant_id"]};{grant.get("grant_donation_amount", 5)};{grant.get("token_local_id", 283)}'
                          for grant in no_checkout_grants]

            cart_query = ','.join(cart_query)

            if not cart_query:
                print(f'** No items left in the {activity.profile}\'s cart')
                continue

            if not options['test']:
                try:
                    remember_your_cart(activity.profile, cart_query, no_checkout_grants, hours)
                    count += 1
                except Exception as e:
                    print(f'!! Failed to sent cart reminder email to {activity.profile}')
                    print(e)

        print(f'\n\nSent {count} emails of {last_activity_by_user.count()} carts')
