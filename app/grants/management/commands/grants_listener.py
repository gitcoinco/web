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
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from dashboard.utils import get_tx_status, has_tx_mined
from grants.models import Grant, Subscription
from marketing.mails import warn_subscription_failed

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("marketing.mails").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SLEEP_TIME = 20


def listen_for_tx(grant, subscription, tx, network, tx_type):
    if grant:
        logger.info("  - grant %d", grant.pk)
        model = grant
    elif subscription:
        logger.info("  - sub %d", subscription.pk)
        model = subscription

    status = 'failure'
    txid = None
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
            # execute alert logic
    else:
        logger.info('tx processing successful')
        if tx_type == 'grant_deploy':
            grant.confirm_grant_deploy(tx_contract_address)
        elif tx_type == 'grant_cancel':
            grant.confirm_grant_cancel()
        redirect(reverse('grants:details', args=(grant.pk, grant.slug)))


class Command(BaseCommand):

    help = 'listens for tx confirmations on chain'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)


    def handle(self, *args, **options):
        # setup
        network = options['network']

        logger.info('grants_listener - Network: (%s)', network)

        unconfirmed_grant_deploy = Grant.objects.filter(contract_address='0x0', deploy_tx_confirmed=False, network=network)
        logger.info("got %d unconfirmed deploy_grant_txs", unconfirmed_grant_deploy.count())

        unconfirmed_grant_cancel = Grant.objects.filter( cancel_tx_confirmed=False, network=network).exclude(cancel_tx_id='0x0').exclude(cancel_tx_id='')
        logger.info("got %d unconfirmed cancel_grant_txs", unconfirmed_grant_cancel.count())

        for grant in unconfirmed_grant_deploy:
            listen_for_tx(grant, None, grant.deploy_tx_id, grant.network, 'grant_deploy')

        for grant in unconfirmed_grant_cancel:
            listen_for_tx(grant, None, grant.cancel_tx_id, network, 'grant_cancel')
