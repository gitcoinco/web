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
from marketing.mails import warn_subscription_failed

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("marketing.mails").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SLEEP_TIME = 20


def listen_deploy_grant_tx(grant, live):
    logger.info("  - grant %d", grant.pk)

        status = 'failure'
        txid = None
        error = ""
            logger.info("   -- *waiting for confirmation* ")
            while not has_tx_mined(grant.deploy_tx_id, grant.network):
                time.sleep(SLEEP_TIME)
                logger.info(f"   -- *waiting {SLEEP_TIME} seconds*")
            while not has_tx_mined(grant.deploy_tx_id, grant.network):
                time.sleep(SLEEP_TIME)
                logger.info(f"   -- *waiting {SLEEP_TIME} seconds*")
                status, __ = get_tx_status(grant.deploy_tx_id, grant.network, timezone.now())
            if status != 'success':
                    error = f"tx status from RPC is {status} not success, txid: {grant.deploy_tx_id}"

        logger.info("   -- *mined* (status: %s / error: %s) ", status, error)
        was_success = status == 'success'
            if not was_success:
                logger.warning('tx processing failed')
                # execute alert logic
            else:
                logger.info('tx processing successful')
                subscription.successful_contribution(txid)
                subscription.save()


class Command(BaseCommand):

    help = 'listens for tx confirmations on chain'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)
    )

    def handle(self, *args, **options):
        # setup
        network = options['network']
        live = options['live']

        logger.info('grants_listener - Network: (%s) Live: (%s)', network, live)

        deploy_grant_txs = Grant.objects.filter(deploy_tx_id__innull=False, deploy_tx_confirmed__isnull=True)
        logger.info("got %d unconfirmed deploy_grant_txs", deploy_grant_txs.count())

        for tx in deploy_grant_txs:
            listen_deploy_grant_tx(grant, live)
