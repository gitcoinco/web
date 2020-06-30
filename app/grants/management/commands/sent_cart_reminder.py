# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Max, F
from django.utils import timezone

from dashboard.utils import get_tx_status, has_tx_mined
from grants.clr import predict_clr
from grants.models import Contribution, Grant, CartActivity, Subscription
from grants.views import clr_active
from marketing.mails import warn_subscription_failed, remember_your_cart
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

    def handle(self, *args, **options):
        mr = MatchRound.objects.current().first()

        if mr:
            valid_to = mr.valid_to
            hours = int((valid_to - datetime.now()).total_seconds() / 3600)
            if hours != 72:
                print(f'This will be executed when left 72 hours, current left {hours}')
                return

            last_activity_by_user = (CartActivity.objects.filter(created_on__lte=valid_to,
                                                                 created_on__gt=mr.valid_from)
                                     .exclude(metadata=[]).values('profile')
                                     .annotate(most_recent=Max('created_on')))

            for activity_dict in last_activity_by_user:
                activity = CartActivity.objects.get(profile_id=activity_dict['profile'],
                                                    created_on=activity_dict['most_recent'])
                print(activity)
                # Check if this cart is still valid
                no_checkout_grants = []
                for grant_entry in activity.metadata:
                    subscription = Subscription.objects.filter(grant_id=grant_entry['grant_id'],
                                                               contributor_profile=activity.profile,
                                                               created_on__gt=activity.created_on,
                                                               created_on__lte=valid_to).first()

                    if not subscription:
                        no_checkout_grants.append(grant_entry)

                if options['full_cart']:
                    if len(no_checkout_grants) != len(activity.metadata):
                        print(f' * Activity {activity.id}: The grants were partially contributed but no notification will be delivered')
                        continue

                cart_query = [f'{grant["grant_id"]};{grant.get("grant_donation_amount", 5)};{grant.get("token_local_id", 283)}'
                              for grant in no_checkout_grants]

                cart_query = ','.join(cart_query)

                if not options['test']:
                    remember_your_cart(activity.profile, cart_query)

        else:
            print('== No matching round active')

        print("finished CLR estimates")
