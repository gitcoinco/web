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
from kudos.models import Token
from eth_utils import to_checksum_address
from web3.middleware import geth_poa_middleware

from functools import wraps

logger = logging.getLogger(__name__)


class KudosError(Exception):
    """Base class for exceptions in this module."""
    pass


class Gen0ExistsWeb3(KudosError):
    pass


class Gen0ExistsDb(KudosError):
    pass


class KudosMismatch(KudosError):
    """ Exception is raised when web3 and the database are out of sync.




        Attributes:
        kudos_id -- the kudos id that has mismatched data
        kudos_web3 -- kudos attributes on web3
        kudos_db -- kudos attritubes in the database
        message -- explanation of the error

    """
    def __init__(self, kudos_id, kudos_web3, kudos_db, message):
        self.kudos_id = kudos_id
        self.kudos_web3 = kudos_web3
        self.kudos_db = kudos_db
        self.message = message


class KudosContract:
    def __init__(self, network='localhost', account=None, private_key=None):
        self.network = network

        self._w3 = get_web3(self.network)
        self._contract = self._get_contract()

        if not account:
            try:
                account = self._w3.eth.accounts[0]
            except IndexError:
                raise RuntimeError('Please specify an account to use for interacting with the Kudos Contract.')

        self.account = to_checksum_address(account)
        self.private_key = private_key
        self.address = self._get_contract_address()

    @staticmethod
    def get_kudos_map(kudos):
        """ Pass in a kudos array that is returned from web3, convert to dictionary.

            Use this to operate on the database.

        """
        return dict(name=kudos[0],
                    description=kudos[1],
                    rarity=kudos[2],
                    price_finney=kudos[3],
                    num_clones_allowed=kudos[4],
                    num_clones_in_wild=kudos[5],
                    tags=kudos[6],
                    image=kudos[7],
                    cloned_from_id=kudos[8],
                    sent_from_address=kudos[9]
                    )

    def sync_db_decorator(f):
        """ Decorator to sync up the database.  Any method that changes the state of the Kudos
            contract should be decorated with `sync_db`.
        """
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            # Get the most recent kudos_id before the function is called
            old_supply = self._contract.functions.totalSupply().call()
            # Run the function
            r = f(self, *args, **kwargs)
            # Handle the dummy Kudos
            if old_supply == 0:
                return r
            # Check the most recent id again
            new_supply = self._contract.functions.totalSupply().call()

            # TODO: If multiple Kudos have been cloned or minted, might be able to optimize
            # this by only doing one database transaction, rather than one for each kudos.
            for kudos_id in range(old_supply, new_supply + 1):
                kudos = self.getKudosById(kudos_id)
                kudos_map = self.get_kudos_map(kudos)
                owner_address = self._contract.functions.ownerOf(kudos_id).call()
                kudos_db = Token(pk=kudos_id, owner_address=owner_address, **kudos_map)
                kudos_map['owner_address'] = owner_address
                kudos_db.save()
                logger.info(f'Synced Kudos ID {kudos_id}: {kudos_map}')

            return r
        return wrapper

    def sync_db(self):
        """ Sync the database with the blockchain.

            During a Kudos clone  or cloneAndTransfer, two rows need to be updated in the
            kudos.Token table.

            1. The new kudos that was just cloned needs to be added.
            2. The gen0 kudos needs to be updated, primarily the num_clones_in_wild field.

            Both of these tasks are accomplished by reading from the Kudos Contract, and then
            running the .save() command to update the Django Database.

            """

        # Part 1.  The newly cloned Kudos.
        kudos_id = self._contract.functions.totalSupply().call()
        # Handle the dummy Kudos
        if kudos_id == 0:
            return False
        owner_address = self._contract.functions.ownerOf(kudos_id).call()
        kudos = self.getKudosById(kudos_id)
        kudos_map = self.get_kudos_map(kudos)
        kudos_db = Token(pk=kudos_id, owner_address=owner_address, **kudos_map)
        kudos_db.save()
        kudos_map['owner_address'] = owner_address
        logger.info(f'Synced Kudos ID {kudos_id}: {kudos_map}')

        # Part 2.  Sync up the Gen0 Kudos.
        kudos_id = kudos_db.cloned_from_id
        owner_address = self._contract.functions.ownerOf(kudos_id).call()
        kudos = self.getKudosById(kudos_id)
        kudos_map = self.get_kudos_map(kudos)
        kudos_db = Token(pk=kudos_id, owner_address=owner_address, **kudos_map)
        kudos_db.save()
        logger.info(f'Synced Kudos ID {kudos_id}: {kudos_map}')

        return True

    def _get_contract_address(self):
        if self.network == 'mainnet':
            return to_checksum_address('')
        elif self.network == 'ropsten':
            return to_checksum_address('0x4cB49D1ed051A55F692253e8036Ad835fD735a20')
        elif self.network == 'rinkeby':
            return to_checksum_address('0x0b9bFF2c5c7c85eE94B48D54F2C6eFa1E399380D')
        else:
            # local testrpc
            return to_checksum_address('0xe7bed272ee374e8116049d0a49737bdda86325b6')
        # raise UnsupportedNetworkException(self.network)

    def _get_contract(self):
        with open('kudos/Kudos.json') as f:
            abi = json.load(f)['abi']
        address = self._get_contract_address()
        return self._w3.eth.contract(address=address, abi=abi)

    # @sync_db_decorator
    def mint(self, *args):
        """ Contract method.

            Mint a new Gen0 Kudos on the blockchain.
            Not to be confused with clone.  A clone() operation is only valid for an already
            existing Gen0 Kudos.

            *args:  See the Kudos.sol for implementation details.

            From Kudos.sol:

            mint(
                string name,
                string description,
                uint256 rarity,
                uint256 priceFinney,
                uint256 numClonesAllowed,
                string tags,
                string image,
                )
        """
        name = args[0]
        if self.gen0_exists_web3(name):
            msg = f'The {name} Gen0 Kudos already exists on the blockchain.'
            logger.warning(msg)
            return False
        if self.gen0_exists_db(name):
            msg = f'The {name} Gen0 Kudos already exists in the database.'
            logger.warning(msg)
            return False

        if self.private_key:
            nonce = self._w3.eth.getTransactionCount(self.account)
            txn = self._contract.functions.mint(*args).buildTransaction({'gas': 700000, 'nonce': nonce, 'from': self.account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=self.private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            tx_hash = self._contract.functions.mint(*args).transact({"from": self.account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)

        self.sync_db()

        return tx_receipt

    def clone(self, *args):
        """ Contract method.

            *args:  See the Kudos.sol for implementation details.

            From Kudos.sol:

            clone(string name, uint256 numClonesRequested)
        """

        if self.private_key:
            nonce = self._w3.eth.getTransactionCount(self.account)
            txn = self._contract.functions.clone(*args).buildTransaction({'gas': 700000, 'nonce': nonce, 'from': self.account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=self.private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            tx_hash = self._contract.functions.clone(*args).transact({"from": self.account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)

        self.sync_db()

        return tx_receipt

    def cloneAndTransfer(self, *args):
        """ Contract method.

            *args:  See the Kudos.sol for implementation details.

            From Kudos.sol:

            cloneAndTransfer(string name, uint256 numClonesRequested, address receiver)
        """
        if self.private_key:
            nonce = self._w3.eth.getTransactionCount(self.account)
            txn = self._contract.functions.cloneAndTransfer(*args).buildTransaction({'gas': 700000, 'nonce': nonce, 'from': self.account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=self.private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            tx_hash = self._contract.functions.cloneAndTransfer(*args).transact({"from": self.account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)

        self.sync_db()

        return tx_receipt

    def burn(self, *args):
        """ Contract method. """
        pass

    def getKudosById(self, *args):
        """ Contract method. """
        return self._contract.functions.getKudosById(args[0]).call()

    def getGen0TokenId(self, *args):
        """ Contract method. """
        return self._contract.functions.getGen0TokenId(args[0]).call()

    def gen0_exists_web3(self, kudos_name):
        """ Helper method.  """
        kudos_id = self.getGen0TokenId(kudos_name)
        logger.info(f'kudos_id: {kudos_id}')
        if kudos_id == 0:
            return False
        else:
            return True

    def gen0_exists_db(self, kudos_name):
        """ Helper method.  """
        kudos_name = Token.objects.filter(name__iexact=kudos_name).first()
        if not kudos_name:
            return False
        else:
            return True

    def sync_status(self):
        pass


# ######################################### LEGACY CODE #########################################
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
    gen0name = Token.objects.filter(name__iexact=name).first()
    if gen0name is not None:
        raise ValueError(f'The {name} Gen0 Kudos already exists in the database.')

    w3 = get_web3(network)

    kudos_contract = getKudosContract(network)
    # logger.info(w3.eth.accounts)
    account = to_checksum_address('0xD386793F1DB5F21609571C0164841E5eA2D33aD8')
    # account = w3.eth.accounts[0]
    # logger.info(f'account: {account}')
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
    # logger.info(f'kudos_id: {kudos_id}')
    kudos = kudos_contract.functions.getKudosById(kudos_id).call()

    logger.info(f'Minted Kudos ID {kudos_id}: {kudos}')

    kudos_map = get_kudos_map(kudos)

    kudos_db = Token(pk=kudos_id, **kudos_map)
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
        kudos_db = Token.objects.get(pk=kudos_id)
    except Token.DoesNotExist:
        return False

    for k, v in kudos_map.items():
        if getattr(kudos_db, k) != v:
            logger.warning(f'Kudos blockchain/db mismatch: {k}')
            mismatch = True

    return mismatch


def update_kudos_db(kudos_id, network):
    kudos = get_kudos_from_web3(kudos_id, network)
    kudos_map = get_kudos_map(kudos)
    kudos_db = Token(pk=kudos_id, **kudos_map)
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
    # logger.info(f'Kudos Gen0 ID: {kudos_id}.  ID of 0 indicates not found.')

    return kudos_id


def clone_kudos(network):
    pass


def clone_and_transfer_kudos_web3(network, private_key=None, *args):
    """ Clone a new Kudos and transfer it to another address.

        private_key:  Optionally pass a private key to sign the transaction locally
        *args:  See the Kudos.sol cloneAndTransfer() function for the propery keyword arguments.

        From Kudos.sol:
        cloneAndTransfer(string name,
                         uint256 numClonesRequested,
                         address receiver,
                         )
    """
    if (settings.DEBUG or settings.ENV != 'prod') and network == 'mainnet':
        # This block will return {} if env isn't prod and the network is mainnet.
        return {}

    w3 = get_web3(network)

    kudos_contract = getKudosContract(network)
    account = to_checksum_address('0xD386793F1DB5F21609571C0164841E5eA2D33aD8')

    w3.eth.defaultAccount = account

    if private_key:
        nonce = w3.eth.getTransactionCount(account)
        txn = kudos_contract.functions.cloneAndTransfer(*args).buildTransaction({'gas': 700000, 'nonce': nonce, 'from': account})
        # logger.info(txn)
        signed_txn = w3.eth.account.signTransaction(txn, private_key=private_key)
        # logger.info(signed_txn)
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # logger.info(f'tx_hash: {tx_hash}')
    else:
        tx_hash = kudos_contract.functions.cloneAndTransfer(*args).transact({"from": account})

    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    # logger.info(f'tx_receipt: {tx_receipt}')
    # logger.info(f'kudos_id: {int(tx_receipt.logs[0].data, 10)}')

    # Normally this would be totalSupply() - 1, but we have a dummy Kudos at index 0
    kudos_id = kudos_contract.functions.totalSupply().call()
    logger.info(f'kudos_id: {kudos_id}')
    kudos = kudos_contract.functions.getKudosById(kudos_id).call()

    logger.info(f'Minted Kudos ID {kudos_id}: {kudos}')

    kudos_map = get_kudos_map(kudos)

    kudos_db = Token(pk=kudos_id, **kudos_map)
    kudos_db.save()

    return kudos


def web3_process_kudos():
    pass


def get_kudos_id():
    pass


def get_kudos_id_from_web3():
    pass

