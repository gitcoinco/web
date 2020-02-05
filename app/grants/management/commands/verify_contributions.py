# -*- coding: utf-8 -*-
"""
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
import logging

from django.core.management.base import BaseCommand

from grants.models import Contribution

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = 'verify contribution transaction against blockchain'

    def add_arguments(self, parser):
        parser.add_argument(
            '-live', '--live', action='store_true', dest='live', default=False, help='Actually mark falsified contributions'
        )

    def handle(self, *args, **options):
        # we can only check contributions that have both approval and split transactions
        contributions = Contribution.objects.exclude(tx_id='0x0').exclude(tx_id='').exclude(split_tx_id='')

        for contribution in contributions:
            valid, reason = contribution.verify_transactions()

            if not valid:
                logger.info(f'Contribution {contribution.pk} seems falsified, reason: {reason}.')

                if options['live']:
                    logger.info(f'Marking contribution {contribution.pk} as failed.')
                    contribution.success = False
                    contribution.save()