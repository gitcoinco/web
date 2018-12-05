# -*- coding: utf-8 -*-
#!/usr/bin/env python3
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
import logging
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.utils import has_tx_mined, get_tx_status
from grants.models import Grant
from marketing.mails import warn_subscription_failed

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("marketing.mails").setLevel(logging.WARNING)


def process_subscription(subscription, live):
    is_ready_to_be_processed_db = subscription.get_is_ready_to_be_processed_from_db()

    print(f"  - subscription {subscription.pk}")
    if is_ready_to_be_processed_db:
        print("   -- (ready via db) ")
        are_we_past_next_valid_timestamp = subscription.get_are_we_past_next_valid_timestamp()

        # FOR DEBUGGING
        if not live:
            is_ready_to_be_processed_web3 = subscription.get_is_subscription_ready_from_web3()
            is_active_web3 = subscription.get_is_active_from_web3()
            signer = subscription.get_subscription_signer_from_web3()
            print("    ---  DEBUG INFO")
            print("    --- ", are_we_past_next_valid_timestamp, is_ready_to_be_processed_web3, is_active_web3, signer)

        if are_we_past_next_valid_timestamp:
            print("   -- (ready via web3) ")
            if not live:
                print("   -- *not live, not executing* ")
            else:
                print("   -- *executing* ")
            status = 'failure'
            txid = None
            error = None
            try:
                if live:
                    txid = subscription.do_execute_subscription_via_web3()
                    print(f"   -- *waiting for mine* (txid {txid}) ")
                    while not has_tx_mined(txid, subscription.grant.network):
                        time.sleep(10)
                        print("   -- *waiting 10 seconds*")
                    status, timestamp = get_tx_status(txid, subscription.grant.network, timezone.now())
            except Exception as e:
                error = str(e)

            print(f"   -- *mined* (status: {status} / error: {error}) ")
            was_success = status == 'success'
            if live:
                if not was_success:
                    warn_subscription_failed(subscription, txid, status, error)
                else:
                    subscription.successful_contribution(txid)
                    subscription.save()


class Command(BaseCommand):

    help = 'processes the txs associated with this grant'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)
        parser.add_argument(
            '-live', '--live',
            action='store_true',
            dest='live',
            default=False,
            help='Actually do the sync'
        )

    def handle(self, *args, **options):
        # setup
        network = options['network']
        live = options['live']

        # iter through Grants
        grants = Grant.objects.filter(network=network)
        print(f"got {grants.count()} grants")

        for grant in grants:
            subs = grant.subscriptions.filter(active=True, next_contribution_date__lt=timezone.now())
            print(f" - {grant.pk} has {subs.count()} subs")

            for subscription in subs:
                process_subscription(subscription, live)
