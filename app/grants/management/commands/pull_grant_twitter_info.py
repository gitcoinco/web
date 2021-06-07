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

from django.conf import settings
from django.core.management.base import BaseCommand

import twitter
from dashboard.utils import get_web3
from grants.models import Grant


class Command(BaseCommand):

    help = 'checks for follower counts on grants profiles, and also does some basic data integrity stuff'

    def handle(self, *args, **kwargs):

        api = twitter.Api(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token_key=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_SECRET,
        )

        for grant in Grant.objects.all():
            try:
                if grant.twitter_handle_1:
                    user = api.GetUser(screen_name=grant.twitter_handle_1.replace('@', ''))
                    grant.twitter_handle_1_follower_count = user.followers_count
                    grant.save()
            except Exception as e:
                print(e)
            try:
                if grant.twitter_handle_2:
                    user = api.GetUser(screen_name=grant.twitter_handle_2.replace('@', ''))
                    grant.twitter_handle_2_follower_count = user.followers_count
                    grant.save()
            except Exception as e:
                print(e)

            try:
                if not grant.contract_owner_address:
                    w3 = get_web3('mainnet')
                    grant.contract_owner_address = w3.eth.getTransaction(grant.deploy_tx_id)['from']
                    grant.save()

            except Exception as e:
                print(e)
