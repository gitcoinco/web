# -*- coding: utf-8 -*-
"""Handle IPFS hash pulling command logic.

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

from dashboard.helpers import UnsupportedSchemaException
from dashboard.utils import (
    BountyNotFoundException, StdBountyRangedCommand, get_ipfs, get_ipfs_hash, get_standard_bounty_id, infura_ipfs_pin,
    ipfs_pin,
)

logger = logging.getLogger(__name__)


class Command(StdBountyRangedCommand):
    """Define the IPFS pulling management command."""

    help = 'pulls the IPFS hashes for bounties within the provided range'

    def handle(self, *args, **options):
        # config
        network = options['network']

        start_id = get_standard_bounty_id(options['start_id'], network)
        end_id = get_standard_bounty_id(options['end_id'], network)

        # iterate through all the bounties
        standard_bounty_id = int(start_id)
        print('syncing from', start_id, 'to', end_id)
        more_bounties = True
        ipfs_client = get_ipfs()

        while more_bounties:
            try:
                # pull and process each bounty
                print('Pulling IPFS hash for:', standard_bounty_id)
                bounty_ipfs_hash = get_ipfs_hash(standard_bounty_id, network)
                print('Pulled standard bounty: ', standard_bounty_id, ' - IPFS hash: ', bounty_ipfs_hash)
                # Pin the provided hash key on Infura.
                infura_ipfs_pin(bounty_ipfs_hash)
                ipfs_pin(bounty_ipfs_hash, ipfs_client)
            except BountyNotFoundException:
                more_bounties = False
            except UnsupportedSchemaException:
                logger.info("* Unsupported Schema", exc_info=True)
            except Exception:
                extra_data = {
                    'standard_bounty_id': standard_bounty_id,
                    'more_bounties': more_bounties,
                    'network': network,
                }
                logger.error('Exception encountered while attempting to pin hashes', exc_info=True, extra=extra_data)
            finally:
                standard_bounty_id += 1
                if standard_bounty_id > int(end_id):
                    more_bounties = False
