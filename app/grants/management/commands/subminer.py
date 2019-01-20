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
import logging
import time

from django.core.management.base import BaseCommand
from django.db.models import F
from django.utils import timezone

from dashboard.utils import get_tx_status, has_tx_mined
from grants.models import Grant
from marketing.mails import warn_subscription_failed

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("marketing.mails").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SLEEP_TIME = 20


def process_subscription(subscription, live):
    is_ready_to_be_processed_db = subscription.get_is_ready_to_be_processed_from_db()

    logger.info("  - subscription %d", subscription.pk)
    if is_ready_to_be_processed_db:
        logger.info("   -- (ready via db) ")
        are_we_past_next_valid_timestamp = subscription.get_are_we_past_next_valid_timestamp()

        # FOR DEBUGGING
        if not live:
            is_ready_to_be_processed_web3 = subscription.get_is_subscription_ready_from_web3()
            is_active_web3 = subscription.get_is_active_from_web3()
            signer = subscription.get_subscription_signer_from_web3()
            logger.info("    ---  DEBUG INFO")
            logger.info(
                "    --- %s, %s, %s, %s", are_we_past_next_valid_timestamp, is_ready_to_be_processed_web3,
                is_active_web3, signer,
            )

        if not are_we_past_next_valid_timestamp:
            logger.info(f"   -- ( NOT ready via web3, will be ready on {subscription.get_next_valid_timestamp()}) ")
        else:
            logger.info("   -- (ready via web3) ")
            status = 'failure'
            txid = None
            error = ""
            try:
                if live:
                    logger.info("   -- *executing* ")
                    while not has_tx_mined(subscription.new_approve_tx_id, subscription.grant.network):
                        time.sleep(SLEEP_TIME)
                        logger.info(f"   -- *waiting {SLEEP_TIME} seconds*")
                    txid = subscription.do_execute_subscription_via_web3()
                    logger.info("   -- *waiting for mine* (txid %s) ", txid)
                    while not has_tx_mined(txid, subscription.grant.network):
                        time.sleep(SLEEP_TIME)
                        logger.info(f"   -- *waiting {SLEEP_TIME} seconds*")
                    status, __ = get_tx_status(txid, subscription.grant.network, timezone.now())
                    if status != 'success':
                        error = f"tx status from RPC is {status} not success, txid: {txid}"
                else:
                    logger.info("   -- *not live, not executing* ")
            except Exception as e:
                error = str(e)
                logger.info("   -- *not live, not executing* ")

            logger.info("   -- *mined* (status: %s / error: %s) ", status, error)
            was_success = status == 'success'
            if live:
                if not was_success:
                    logger.warning('subscription processing failed')
                    subscription.error = True
                    error_comments = f"{error}\n\ndebug info: {subscription.get_debug_info()}"
                    subscription.subminer_comments = error_comments
                    subscription.save()
                    warn_subscription_failed(subscription)
                else:
                    logger.info('subscription processing successful')
                    subscription.successful_contribution(txid)
                    subscription.save()


class Command(BaseCommand):

    help = 'processes the txs associated with this grant'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)
        parser.add_argument(
            '-live', '--live', action='store_true', dest='live', default=False, help='Actually do the sync'
        )

    def handle(self, *args, **options):
        # setup
        network = options['network']
        live = options['live']

        logger.info('Subminer - Network: (%s) Live: (%s)', network, live)
        # iter through Grants
        grants = Grant.objects.filter(network=network).active()
        logger.info("got %d grants", grants.count())

        for grant in grants:
            subs = grant.subscriptions.filter(
                active=True,
                error=False,
                next_contribution_date__lt=timezone.now(),
                num_tx_processed__lt=F('num_tx_approved')
            )
            logger.info(" - %d has %d subs ready for execution", grant.pk, subs.count())

            for subscription in subs:
                process_subscription(subscription, live)
