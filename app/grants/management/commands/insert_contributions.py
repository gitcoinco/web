# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

Copyright (C) 2018 Gitcoin Core

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

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'inserts contributions into the DB'

    def handle(self, *args, **options):
        # setup
        handle = 'igorbarinov'
        token_addr = '0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359'
        contributor_address = '0x34aa3f359a9d614239015126635ce7732c18fdf3'
        token_symbol = 'DAI'
        network = 'mainnet'

        from dashboard.models import Profile
        from grants.models import Grant, Contribution, Subscription
        from grants.views import record_subscription_activity_helper
        items = [[114, 10000, '0x51d9e5b1667b716ccd3c3247b14eec03b92beb91d57c1708e7700a01cebfb4ee']]

        for item in items:
            grant_id = item[0]
            amount = item[1]
            tx_id = item[2]
            print(grant_id)
            grant = Grant.objects.get(pk=grant_id)
            profile = Profile.objects.get(handle=handle)
            subscription = Subscription()

            subscription.active = False
            subscription.contributor_address = contributor_address
            subscription.amount_per_period = amount
            subscription.real_period_seconds = 0
            subscription.frequency = 1
            subscription.frequency_unit = 'days'
            subscription.token_address = token_addr
            subscription.token_symbol = token_symbol
            subscription.gas_price = 1
            subscription.new_approve_tx_id = '0x0'
            subscription.num_tx_approved = 1
            subscription.network = network
            subscription.contributor_profile = profile
            subscription.grant = grant
            subscription.save()

            subscription.successful_contribution(tx_id);
            subscription.error = True #cancel subs so it doesnt try to bill again
            subscription.subminer_comments = "skipping subminer bc this is a 1 and done subscription, and tokens were alredy sent"
            subscription.save()
            record_subscription_activity_helper('new_grant_contribution', subscription, profile)
