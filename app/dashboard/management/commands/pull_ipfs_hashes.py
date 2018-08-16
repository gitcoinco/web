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

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.helpers import UnsupportedSchemaException
from dashboard.utils import BountyNotFoundException, get_ipfs, getBountyContract, infura_ipfs_pin, ipfs_pin

logger = logging.getLogger(__name__)
default_start_id = 0 if not settings.DEBUG else 402


def get_bounty_id(_id, network):
    if _id > 0:
        return _id
    contract = getBountyContract(network)
    bounty_id = contract.functions.getNumBounties().call() - 1
    return bounty_id + _id


def get_ipfs_hash(standard_bounty_id, network='rinkeby'):
    """Get the IPFS hash of the provided standard bounties ID.

    Args:
        standard_bounty_id (int): The standard bounty ID.
        network (str): The network to lookup. Defaults to: mainnet.

    Returns:
        str: The IPFS hash.

    """
    if (settings.DEBUG or settings.ENV != 'prod') and network == 'mainnet':
        return ''

    try:
        standard_bounties = getBountyContract(network)
        ipfs_hash = standard_bounties.functions.getBountyData(standard_bounty_id).call()
        return ipfs_hash
    except Exception as e:
        logger.error(e)
        return ''


class Command(BaseCommand):
    """Define the IPFS pulling management command."""

    help = 'pulls the IPFS hashes for bounties within the provided range'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)
        parser.add_argument(
            'start_id',
            default=default_start_id,
            type=int,
            help="The start id.  If negative or 0, will be set to highest bounty id minus <x>"
        )
        parser.add_argument(
            'end_id',
            default=99999999999,
            type=int,
            help="The end id.  If negative or 0, will be set to highest bounty id minus <x>"
        )

    def handle(self, *args, **options):
        # config
        network = options['network']

        start_id = get_bounty_id(options['start_id'], network)
        end_id = get_bounty_id(options['end_id'], network)

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
                logger.error('Failed to fetch github username', exc_info=True, extra=extra_data)
            finally:
                standard_bounty_id += 1
                if standard_bounty_id > int(end_id):
                    more_bounties = False
