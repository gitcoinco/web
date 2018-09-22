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
from kudos.models import Token, KudosTransfer
from eth_utils import to_checksum_address, to_normalized_address, to_text
from web3.middleware import geth_poa_middleware
from django.forms.models import model_to_dict

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

    """A class represending the Kudos.sol contract.

    Note: There are two types of interactions that can be done on the Solidity contract,
    - call()
    - transact()

    A call() is just a getter, and does not require gas, or an account to transact with.
    A transact() or transaction requires gas and typically changes state on the contract.

        A transaction requires an account, because it needs somewhere to pull the gas from.
        When working in Javascript and web3js, Metamask is used to handle this interaction.
        When working in Python and web3py, there is no interaction with MetaMask so this
        needs to be handled behind the scenes, by providing the account and private_key to
        web3py to create the raw transaction.

    Attributes:
        network (str): The blockchain network (localhost, rinkeby, ropsten, mainnet)
        address (str): The addess of the Kudos.sol contract on the blockchain.
    """

    def __init__(self, network='localhost'):
        """Initialize the KudosContract.

        Args:
            network (str, optional): The blockchain network (localhost, rinkeby, ropsten, mainnet)

        """
        self.network = network

        self._w3 = get_web3(self.network)
        self._contract = self._get_contract()

        self.address = self._get_contract_address()

    @staticmethod
    def get_kudos_map(kudos):
        """Pass in a kudos array that is returned from web3, convert to dictionary.

        Use this to operate on the database.

        Args:
            kudos (list): A kudos object returned from the Kudos.sol contract.  Soldidity returns
                          the Kudos strcut as an array.

        Returns:
            dict: Kudos dictionary with key/values to be used to interact with the database.

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
                    # sent_from_address=kudos[9]
                    )

    def may_require_key(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self.network != 'localhost' and (kwargs['account'] is None or kwargs['private_key'] is None):
                raise ValueError(f'Since you are on the {self.network} network, you must provide and account and private_key')
            else:
                return f(self, *args, **kwargs)
        return wrapper

    def reconcile_db(self, start_id=1):
        """Sync up existing kudos from the blockchain to the database.

        Then remove all "orphaned Kudos" from the database.
        """

        latest_id = self._contract.functions.totalSupply().call()
        for kudos_id in range(start_id, latest_id):
            self.sync_kudos_db(kudos_id=kudos_id)

        # Remove orphaned Kudos in the database
        Token.objects.filter(pk__gt=latest_id).delete()

    def sync_kudos_db(self, kudos_id):
        kudos = self.getKudosById(kudos_id, to_dict=True)

        kudos['owner_address'] = self._contract.functions.ownerOf(kudos_id).call()
        kudos_token = Token(pk=kudos_id, **kudos)
        if not Token.objects.filter(pk=kudos_id).exists():
            kudos_token.save()
        else:
            # Make sure to not overwrite the sent_from_adderss field.
            kudos_token.save(update_fields=list(kudos.keys()))
        logger.info(f'Synced id #{kudos_token.id}, "{kudos_token.name}" kudos to the database.')
        return kudos_token

    def sync_transferred_kudos_db(self, kudos_id, tx_hash):
        # Handle the dummy Kudos
        if kudos_id == 0:
            return False
        kudos = self.getKudosById(kudos_id, to_dict=True)
        kudos['owner_address'] = self._contract.functions.ownerOf(kudos_id).call()
        kudos_token = Token(pk=kudos_id, **kudos)
        kudos_token.save()

        # For the case of the Kudos Indirect Send, we need to update the `sent_from_address` field 
        # with the value from the kudos_transfer model.  We want to make sure its the address of the
        # originating sender, not the temporary holding account.

        # Find the object which matches the kudos that was just cloned
        # Now works for both Direct and Indirect Send
        kudos_transfer = KudosTransfer.objects.get(txid__iexact=tx_hash)
        # Store the foreign key reference
        kudos_transfer.kudos_token = kudos_token
        # Set the proper sent_from_address in the kudos_token (overwrite the temporary address)
        kudos_token.sent_from_address = kudos_transfer.from_address
        # Also need to set the owner_address
        kudos_token.owner_address = self._contract.functions.ownerOf(kudos_id).call()

        kudos_transfer.save()
        kudos_token.save()

        logger.info(f'Synced id #{kudos_token.id}, "{kudos_token.name}" kudos to the database.')

        # Sync up the Gen0 Kudos
        self.sync_kudos_db(kudos_id)
        return True

    def update_kudos_db(self, kudos_id, tx_hash):
        pass

    def _get_contract_address(self):
        """Get the Kudos contract address, depending on the network.

        Returns:
            str: Kudos contract address.
        """
        if self.network == 'mainnet':
            return to_checksum_address('')
        elif self.network == 'ropsten':
            return to_checksum_address('0xb5e880859dbe23793d5b6be2c5547001c4b97af8')
        elif self.network == 'rinkeby':
            return to_checksum_address('0x0b9bFF2c5c7c85eE94B48D54F2C6eFa1E399380D')
        else:
            # local testrpc
            return to_checksum_address('0xe7bed272ee374e8116049d0a49737bdda86325b6')
        # raise UnsupportedNetworkException(self.network)

    def _get_contract(self):
        """Load up the Kudos ABI from a .json file.

        Returns:
            obj: Web3py contract object.
        """
        with open('kudos/Kudos.json') as f:
            abi = json.load(f)
        address = self._get_contract_address()
        return self._w3.eth.contract(address=address, abi=abi)

    def _resolve_account(self, account):
        """
        This method will return one of the following:
            - the checksummed account address if the account is given
            - the local account if it can find it
            - raise an error if it can't resolve the account

        Args:
            account (str): The ethereum public account address.

        """
        if account:
            return to_checksum_address(account)
        else:
            try:
                return self._w3.eth.accounts[0]
            except IndexError:
                raise RuntimeError('Please specify an account to use for transacting with the Kudos Contract.')

    @may_require_key
    def mint(self, *args, account=None, private_key=None):
        """Contract transaction method.

        Mint a new Gen0 Kudos on the blockchain.  Not to be confused with clone.
        A clone() operation is only valid for an already existing Gen0 Kudos.

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

        Args:
            *args: From Kudos.sol:
            mint(
                string name,
                string description,
                uint256 rarity,
                uint256 priceFinney,
                uint256 numClonesAllowed,
                string tags,
                string image,
                )
            account (str, optional): Public account address.  Not needed for localhost testing.
            private_key (str, optional): Private key for account.  Not needed for localhost testing.

        Returns:
            TYPE: If a sync did occur, returns the tx_receive as a str.
                  If no sync occured, return False.
        """
        account = self._resolve_account(account)

        name = args[0]
        if self.gen0_exists_web3(name):
            logger.warning(f'The "{name}" Gen0 Kudos already exists on the blockchain.  Updating db...')
            kudos_id = self.getGen0TokenId(name)
            self.sync_kudos_db(kudos_id=kudos_id)
            return False

        if private_key:
            logger.debug('Private key found, creating raw transaction for Kudos mint...')
            nonce = self._w3.eth.getTransactionCount(account)
            gas_estimate = self._contract.functions.mint(*args).estimateGas({'nonce': nonce, 'from': account})
            logger.debug(f'Gas estimate : {gas_estimate}')
            txn = self._contract.functions.mint(*args).buildTransaction({'gas': gas_estimate, 'nonce': nonce, 'from': account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            logger.debug('No private key provided, using local signing...')
            tx_hash = self._contract.functions.mint(*args).transact({"from": account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
        logger.debug(f'Tx hash: {tx_hash}')

        kudos_id = self.getGen0TokenId(name)
        logger.info(f'Minted id #{kudos_id}, "{name}" kudos on the blockchain.')

        self.sync_kudos_db(kudos_id=kudos_id)

        return kudos_id

    @may_require_key
    def clone(self, *args, account=None, private_key=None):
        """Contract transaction method.

        Args:
            *args: From Kudos.sol
            clone(string name, uint256 numClonesRequested)
            account (str, optional): Public account address.  Not needed for localhost testing.
            private_key (str, optional): Private key for account.  Not needed for localhost testing.

        Returns:
            str: The tx_receipt.
        """
        account = self._resolve_account(account)

        if private_key:
            nonce = self._w3.eth.getTransactionCount(account)
            txn = self._contract.functions.clone(*args).buildTransaction({'gas': 700000, 'nonce': nonce, 'from': account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            tx_hash = self._contract.functions.clone(*args).transact({"from": account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)

        kudos_id = self._contract.functions.totalSupply().call()
        self.sync_transferred_kudos_db(kudosid=kudos_id, tx_hash=tx_hash)

        return tx_receipt

    @may_require_key
    def cloneAndTransfer(self, *args, account=None,  private_key=None):
        """Contract transaction method.

        Args:
            *args: From Kudos.sol:
            cloneAndTransfer(string name, uint256 numClonesRequested, address receiver)
            account (str, optional): Public account address.  Not needed for localhost testing.
            private_key (str, optional): Private key for account.  Not needed for localhost testing.

        Returns:
            str: The tx_receipt.
        """
        account = self._resolve_account(account)

        if private_key:
            nonce = self._w3.eth.getTransactionCount(account)
            txn = self._contract.functions.cloneAndTransfer(*args).buildTransaction({'gas': 700000, 'nonce': nonce, 'from': account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            tx_hash = self._contract.functions.cloneAndTransfer(*args).transact({"from": account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)

        kudos_id = self._contract.functions.totalSupply().call()
        self.sync_transferred_kudos_db(kudosid=kudos_id, tx_hash=tx_hash)

        return tx_receipt

    def burn(self, *args):
        """ Contract method. """
        pass

    def getKudosById(self, *args, to_dict=False):
        """Contract call method.

        Args:
            *args: From Kudos.sol:
            getKudosById(uint256 tokenId)

        Returns:
            list: From Kudos.sol:
            returns (string name, string description, uint256 rarity,
                     uint256 priceFinney, uint256 numClonesAllowed,
                     uint256 numClonesInWild, string tags, string image,
                     uint256 clonedFromId
                     )
        """
        kudos = self._contract.functions.getKudosById(args[0]).call()
        if to_dict:
            return self.get_kudos_map(kudos)
        else:
            return kudos

    def getGen0TokenId(self, *args):
        """Contract call method.

        Args:
            *args: From Kudos.sol
            getGen0Tokenid(string name)

        Returns:
            int: From Kudos.sol:
            returns (unint256)
        """
        return self._contract.functions.getGen0TokenId(args[0]).call()

    def gen0_exists_web3(self, kudos_name):
        """Helper method.

        Args:
            kudos_name (TYPE): Description

        Returns:
            TYPE: Description
        """
        kudos_id = self.getGen0TokenId(kudos_name)
        # logger.info(f'kudos_id: {kudos_id}')
        if kudos_id == 0:
            return False
        else:
            return True

    def gen0_exists_db(self, kudos_name):
        """Helper method.

        Args:
            kudos_name (TYPE): Description

        Returns:
            TYPE: Description
        """
        kudos_name = Token.objects.filter(name__iexact=kudos_name).first()
        if not kudos_name:
            return False
        else:
            return True

    def sync_status(self):
        pass
