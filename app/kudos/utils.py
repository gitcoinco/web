# -*- coding: utf-8 -*-
"""Define Dashboard related utilities and miscellaneous logic.

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
import json
import logging
import subprocess
import time

from django.conf import settings

from dashboard.utils import UnsupportedNetworkException
from dashboard.utils import get_web3
from kudos.models import MarketPlaceListing
from eth_utils import to_checksum_address

logger = logging.getLogger(__name__)


def get_kudos_map(kudos):
    return dict(name=kudos[0],
                description=kudos[1],
                rarity=kudos[2],
                price=kudos[3],
                num_clones_allowed=kudos[4],
                num_clones_in_wild=kudos[5],
                lister=kudos[6],
                tags=kudos[7],
                image=kudos[8],
                )


def getKudosContractAddress(network):
    if network == 'mainnet':
        return to_checksum_address('')
    elif network == 'ropsten':
        return to_checksum_address('')
    elif network == 'rinkeby':
        return to_checksum_address('0x0b9bFF2c5c7c85eE94B48D54F2C6eFa1E399380D')
    else:
        return to_checksum_address('0xe7bed272ee374e8116049d0a49737bdda86325b6')
    # raise UnsupportedNetworkException(network)


# http://web3py.readthedocs.io/en/latest/contracts.html
def getKudosContract(network):
    web3 = get_web3(network)
    with open('kudos/Kudos.json') as f:
        abi = json.load(f)['abi']
    address = getKudosContractAddress(network)
    contract = web3.eth.contract(address=address, abi=abi)

    return contract


def get_kudos_from_web3(kudos_id, network='localhost'):
    """ Get kudos artifact info from the blockchain. """
    if (settings.DEBUG or settings.ENV != 'prod') and network == 'mainnet':
        # This block will return {} if env isn't prod and the network is mainnet.
        return {}

    kudos_contract = getKudosContract(network)

    # logger.info(kudos_contract.all_functions())
    kudos = kudos_contract.functions.getKudosById(kudos_id).call()
    logger.info(f'Kudos ID {kudos_id}: {kudos}')

    return kudos


def mint_kudos_on_web3_and_db(network, *args):
    """ Mint a new Gen0 Kudos on the blockchain and save it to the database.
        Not to be confused with clone_kudos.

        *args:  See the Kudos.sol create() function for the propery keyword arguments.

        From Kudos.sol:

        create(string name,
               string description,
               uint256 rarity,
               uint256 price,
               uint256 numClonesAllowed,
               string tags,
               string iamge,  // IPFS Hash
               )
    """

    if (settings.DEBUG or settings.ENV != 'prod') and network == 'mainnet':
        # This block will return {} if env isn't prod and the network is mainnet.
        return {}

    web3 = get_web3(network)

    kudos_contract = getKudosContract(network)
    web3.eth.defaultAccount = web3.eth.accounts[0]

    tx_hash = kudos_contract.functions.mint(*args).transact({"from": web3.eth.accounts[0]})
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

    kudos_id = kudos_contract.functions.totalSupply().call() - 1
    kudos = kudos_contract.functions.getKudosById(kudos_id).call()

    logger.info(f'Minted Kudos ID {kudos_id}: {kudos}')

    kudos_map = get_kudos_map(kudos)

    kudos_db = MarketPlaceListing(pk=kudos_id, **kudos_map)
    kudos_db.save()

    # return kudos


def kudos_has_changed(kudos_id):
    """ Given the kudos artifact info obtained from the blockchain, check if it matches
        the database entry.

    Args:
        kudos (list): A kudos array obtained by calling the get_kudos_from_web3() function.

    Returns:
        boolean:  True if the kudos has changed on the blockchain relative to the database.
                  False otherwise.
    """
    mismatch = False
    kudos = get_kudos_from_web3(kudos_id)
    kudos_map = get_kudos_map(kudos)
    kudos_db = MarketPlaceListing.objects.get(pk=kudos_id)

    for k, v in kudos_map.items():
        if getattr(kudos_db, k) != v:
            logger.warning(f'Kudos blockchain/db mismatch: {k}')
            mismatch = True

    return mismatch


def update_kudos_db(kudos_id):
    kudos = get_kudos_from_web3(kudos_id)
    kudos_map = get_kudos_map(kudos)
    kudos_db = MarketPlaceListing(pk=kudos_id, **kudos_map)
    logger.info(f'Updating Kudos ID: {kudos_id}')
    logger.info(json.dumps(kudos_map))
    # Update the database entry
    kudos_db.save()


def get_gen0_id_from_web3(kudos_name, network='localhost'):
    """ Get the kudos id of the Gen0 Kudos using the name.  This information is pulled from web3.

    Args:
        kudos_name (str): The "name" field of the Gen0 Kudos.  This is the same value in the database
                          as the web3 contract.
        network (str, optional): The network we are working on.

    Returns:
        int: Kudos ID.  This maps to the pk in the database.
    """
    if (settings.DEBUG or settings.ENV != 'prod') and network == 'mainnet':
        # This block will return {} if env isn't prod and the network is mainnet.
        return {}

    kudos_contract = getKudosContract(network)

    kudos_id = kudos_contract.functions.getGen0TokenId(kudos_name).call()
    logger.info(f'Kudos Gen0 ID {kudos_id}')

    return kudos_id


def clone_kudos(network):
    pass


def web3_process_kudos():
    pass


def get_kudos_id():
    pass


def get_kudos_id_from_web3():
    pass


