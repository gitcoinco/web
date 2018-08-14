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
from web3.middleware import geth_poa_middleware

logger = logging.getLogger(__name__)


def get_kudos_map(kudos):
    return dict(name=kudos[0],
                description=kudos[1],
                rarity=kudos[2],
                price=kudos[3],
                num_clones_allowed=kudos[4],
                num_clones_in_wild=kudos[5],
                owner_address=kudos[6],
                tags=kudos[7],
                image=kudos[8],
                cloned_from_id=kudos[9],
                )


def getKudosContractAddress(network):
    if network == 'mainnet':
        return to_checksum_address('')
    elif network == 'ropsten':
        return to_checksum_address('0x1aa9f0928c4b9cdd9706bcd4ebabbeafc62e472a')
    elif network == 'rinkeby':
        return to_checksum_address('0x0b9bFF2c5c7c85eE94B48D54F2C6eFa1E399380D')
    else:
        # local testrpc
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


def get_kudos_from_web3(kudos_id, network):
    """ Get kudos artifact info from the blockchain. """
    if (settings.DEBUG or settings.ENV != 'prod') and network == 'mainnet':
        # This block will return {} if env isn't prod and the network is mainnet.
        return {}

    kudos_contract = getKudosContract(network)

    # logger.info(kudos_contract.all_functions())
    kudos = kudos_contract.functions.getKudosById(kudos_id).call()
    logger.info(f'Kudos ID {kudos_id}: {kudos}')

    return kudos


def mint_kudos_on_web3_and_db(network, private_key=None, *args):
    """ Mint a new Gen0 Kudos on the blockchain and save it to the database.
        Not to be confused with clone_kudos.

        private_key:  Optionally pass a private key to sign the transaction locally
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

    name = args[0].lower()
    logger.info(name)

    # Check if Gen0 name already exists on web3.
    gen0id = get_gen0_id_from_web3(name, network)
    if gen0id != 0:
        raise ValueError(f'The {name} Gen0 Kudos already exists on the blockchain.')

    # Check if Gen0 name already exists in the database.
    gen0name = MarketPlaceListing.objects.filter(name__iexact=name).first()
    if gen0name is not None:
        raise ValueError(f'The {name} Gen0 Kudos already exists in the database.')

    w3 = get_web3(network)

    kudos_contract = getKudosContract(network)
    logger.info(w3.eth.accounts)
    account = to_checksum_address('0xD386793F1DB5F21609571C0164841E5eA2D33aD8')
    # account = w3.eth.accounts[0]
    logger.info(f'account: {account}')
    w3.eth.defaultAccount = account
    # logger.info(kudos_contract.all_functions())
    # logger.info(kudos_contract.functions.ownerOf(0).call())

    # logger.info(w3.eth.getBlock('latest'))
    # logger.info(w3.eth.getCode(getKudosContractAddress(network)))

    # w3.middleware_stack.inject(geth_poa_middleware, layer=0)
    # logger.info(w3.version.node)

    if private_key:
        nonce = w3.eth.getTransactionCount(account)
        txn = kudos_contract.functions.mint(*args).buildTransaction({'gas': 700000, 'nonce': nonce, 'from': account})
        # logger.info(txn)
        signed_txn = w3.eth.account.signTransaction(txn, private_key=private_key)
        # logger.info(signed_txn)
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # logger.info(f'tx_hash: {tx_hash}')
    else:
        tx_hash = kudos_contract.functions.mint(*args).transact({"from": account})

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    # logger.info(f'tx_receipt: {tx_receipt}')
    # logger.info(f'kudos_id: {int(tx_receipt.logs[0].data, 10)}')

    # Normally this would be totalSupply() - 1, but we have a dummy Kudos at index 0
    kudos_id = kudos_contract.functions.totalSupply().call()
    logger.info(f'kudos_id: {kudos_id}')
    kudos = kudos_contract.functions.getKudosById(kudos_id).call()

    logger.info(f'Minted Kudos ID {kudos_id}: {kudos}')

    kudos_map = get_kudos_map(kudos)

    kudos_db = MarketPlaceListing(pk=kudos_id, **kudos_map)
    kudos_db.save()

    return kudos


def kudos_exists_web3(kudos_id, network='ropsten'):
    w3 = get_web3(network)
    kudos_contract = getKudosContract(network)


def kudos_exists_db(kudos_id):
    pass


def kudos_has_changed(kudos_id, network):
    """ Given the kudos artifact info obtained from the blockchain, check if it matches
        the database entry.

    Args:
        kudos (list): A kudos array obtained by calling the get_kudos_from_web3() function.

    Returns:
        boolean:  True if the kudos has changed on the blockchain relative to the database.
                  False otherwise.
    """
    mismatch = False
    try:
        kudos = get_kudos_from_web3(kudos_id, network)
    except ValueError:
        return False
    kudos_map = get_kudos_map(kudos)
    try:
        kudos_db = MarketPlaceListing.objects.get(pk=kudos_id)
    except MarketPlaceListing.DoesNotExist:
        return False

    for k, v in kudos_map.items():
        if getattr(kudos_db, k) != v:
            logger.warning(f'Kudos blockchain/db mismatch: {k}')
            mismatch = True

    return mismatch


def update_kudos_db(kudos_id, network):
    kudos = get_kudos_from_web3(kudos_id, network)
    kudos_map = get_kudos_map(kudos)
    kudos_db = MarketPlaceListing(pk=kudos_id, **kudos_map)
    logger.info(f'Updating Kudos ID: {kudos_id}')
    logger.info(json.dumps(kudos_map))
    # Update the database entry
    kudos_db.save()


def get_gen0_id_from_web3(kudos_name, network):
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
    logger.info(f'Kudos Gen0 ID: {kudos_id}.  ID of 0 indicates not found.')

    return kudos_id


def clone_kudos(network):
    pass


def web3_process_kudos():
    pass


def get_kudos_id():
    pass


def get_kudos_id_from_web3():
    pass

