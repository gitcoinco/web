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
from grants.models import Grant, Subscription
from marketing.mails import (
    grant_cancellation, new_grant, new_supporter, subscription_terminated, support_cancellation,
    thank_you_for_supporting, warn_subscription_failed,
)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("marketing.mails").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SLEEP_TIME = 20
MAX_COUNTER = 30


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
                    counter = 0
                    while not has_tx_mined(subscription.new_approve_tx_id, subscription.grant.network):
                        time.sleep(SLEEP_TIME)
                        logger.info(f"   -- *waiting {SLEEP_TIME} seconds for {subscription.new_approve_tx_id} to mine*")
                        counter += 1
                        if counter > MAX_COUNTER:
                            raise Exception(f"waited more than {MAX_COUNTER} times for tx  to mine")

                    txid = subscription.do_execute_subscription_via_web3()
                    logger.info("   -- *waiting for mine* (txid %s) ", txid)

                    override = False
                    counter = 0
                    while not has_tx_mined(txid, subscription.grant.network) and not override:
                        time.sleep(SLEEP_TIME)
                        logger.info(f"   -- *waiting {SLEEP_TIME} seconds for {txid} to mine*")
                        counter += 1
                        if counter > MAX_COUNTER:
                            override = True
                            # force the subminer to continue on; this tx is taking too long.
                            # an admin will have to look at this later and determine what went wrong
                            # KO 2019/02/06

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


def listen_for_tx(grant, subscription, tx, network, tx_type):
    if grant:
        logger.info("  - grant %d %s", grant.pk, tx_type)
    elif subscription:
        logger.info("  - sub %d %s", subscription.pk, tx_type)

    status = 'failure'
    error = "none"
    logger.info("   -- *waiting for confirmation* ")
    while not has_tx_mined(tx, network):
        time.sleep(SLEEP_TIME)
        logger.info(f"   -- *waiting {SLEEP_TIME} seconds*")
    status, __, tx_contract_address = get_tx_status(tx, network, timezone.now())
    if status != 'success':
        error = f"tx status from RPC is {status} not success, txid: {tx}"

    logger.info("   -- *mined* (status: %s / error: %s) ", status, error)
    was_success = status == 'success'
    if not was_success:
        logger.warning('tx processing failed')
        if tx_type == 'grant_deploy':
            transaction_failed(grant, subscription, "Grant Deployment")
        elif tx_type == 'grant_cancel':
            transaction_failed(grant, subscription, "Grant Cancellation")
        elif tx_type == 'new_approve':
            transaction_failed(grant, subscription, "New Approval")
        elif tx_type == 'end_approve':
            transaction_failed(grant, subscription, "End Approval")
        elif tx_type == 'sub_cancel':
            transaction_failed(grant, subscription, "Subscription Cancellation")
    else:
        logger.info('tx processing successful')
        if tx_type == 'grant_deploy':
            grant.confirm_grant_deploy(tx_contract_address)
            new_grant(grant, grant.admin_profile)
        elif tx_type == 'grant_cancel':
            subscriptions = grant.subscriptions.filter(active=True, error=False)
            grant.confirm_grant_cancel()
            grant_cancellation(grant)
            for sub in subscriptions:
                subscription_terminated(grant, sub)
        elif tx_type == 'new_approve':
            subscription.confirm_new_approve()
            new_supporter(subscription.grant, subscription)
            thank_you_for_supporting(subscription.grant, subscription)
        elif tx_type == 'end_approve':
            subscription.confirm_end_approve()
        elif tx_type == 'sub_cancel':
            subscription.confirm_sub_cancel()
            support_cancellation(subscription.grant, subscription)


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
            if subs.count() > 0:
                logger.info(" - %d has %d subs ready for execution", grant.pk, subs.count())

            for subscription in subs:
                try:
                    process_subscription(subscription, live)
                except Exception as e:
                    logger.exception(e)

        unconfirmed_grant_deploy = Grant.objects.filter(
            active=False,
            contract_address='0x0',
            deploy_tx_confirmed=False,
            network=network
        )
        logger.info("got %d unconfirmed deploy_grant_txs", unconfirmed_grant_deploy.count())

        for grant in unconfirmed_grant_deploy:
            listen_for_tx(grant, None, grant.deploy_tx_id, grant.network, 'grant_deploy')

        unconfirmed_grant_cancel = Grant.objects.filter(
            active=True,
            cancel_tx_confirmed=False,
            network=network
        ).exclude(cancel_tx_id='0x0').exclude(cancel_tx_id='')
        logger.info("got %d unconfirmed cancel_grant_txs", unconfirmed_grant_cancel.count())

        for grant in unconfirmed_grant_cancel:
            listen_for_tx(grant, None, grant.cancel_tx_id, network, 'grant_cancel')

        unconfirmed_new_approve = Subscription.objects.filter(
            active=False,
            new_approve_tx_confirmed=False,
            network=network
        ).exclude(new_approve_tx_id='0x0').exclude(new_approve_tx_id='')
        logger.info("got %d unconfirmed new_approve_txs", unconfirmed_new_approve.count())

        for sub in unconfirmed_new_approve:
            listen_for_tx(None, sub, sub.new_approve_tx_id, network, 'new_approve')

        unconfirmed_end_approve = Subscription.objects.filter(
            active=True,
            end_approve_tx_confirmed=False,
            network=network
        ).exclude(end_approve_tx_id='0x0').exclude(end_approve_tx_id='')
        logger.info("got %d unconfirmed end_approve_txs", unconfirmed_end_approve.count())

        for sub in unconfirmed_end_approve:
            listen_for_tx(None, sub, sub.end_approve_tx_id, network, 'new_approve')

        unconfirmed_sub_cancel = Subscription.objects.filter(
            active=True,
            cancel_tx_confirmed=False,
            network=network
        ).exclude(cancel_tx_id='0x0').exclude(cancel_tx_id='')
        logger.info("got %d unconfirmed cancel_sub_txs", unconfirmed_sub_cancel.count())

        for sub in unconfirmed_sub_cancel:
            listen_for_tx(None, sub, sub.cancel_tx_id, network, 'sub_cancel')
