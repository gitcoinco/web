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
from dashboard.utils import get_web3, get_ipfs
from kudos.models import Token, KudosTransfer
from eth_utils import to_checksum_address, to_normalized_address, to_text
from web3.middleware import geth_poa_middleware
from django.forms.models import model_to_dict
from web3.exceptions import BadFunctionCallOutput
from web3.middleware import geth_poa_middleware

from ipfsapi.exceptions import CommunicationError
import ipfsapi

from functools import wraps

logger = logging.getLogger(__name__)


class KudosError(Exception):
    """Base class for exceptions in this module."""
    pass


class KudosTransferNotFound(KudosError):
    """ Exception is raised when web3 and the database are out of sync.


        Attributes:
        kudos_id -- the kudos id that has mismatched data
        message -- explanation of the error

    """
    def __init__(self, kudos_id, message):
        self.kudos_id = kudos_id
        self.message = message


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
        network = 'localhost' if network == 'custom network' else network
        self.network = network

        self._w3 = get_web3(self.network)
        if self.network == 'rinkeby':
            self._w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        host = f'{settings.IPFS_API_SCHEME}://{settings.IPFS_HOST}'
        self._ipfs = ipfsapi.connect(host=host, port=settings.IPFS_API_PORT)
        self._contract = self._get_contract()

        self.address = self._get_contract_address()

    @staticmethod
    def get_kudos_map(kudos, metadata):
        """Pass in a kudos array that is returned from web3, convert to dictionary.

        Use this to operate on the database.

        Args:
            kudos (list): A kudos object returned from the Kudos.sol contract.  Soldidity returns
                          the Kudos strcut as an array.
            metadata (dict):  The metadata return from the tokenURI.

        Returns:
            dict: Kudos dictionary with key/values to be used to interact with the database.

        """
        mapping = dict(price_finney=kudos[0],
                       num_clones_allowed=kudos[1],
                       num_clones_in_wild=kudos[2],
                       cloned_from_id=kudos[3],
                       )

        attributes = metadata.pop('attributes')
        mapping['tags'] = attributes['tags']
        mapping['rarity'] = attributes['rarity']

        # Add the rest of the fields
        kudos_map = {**mapping, **metadata}

        return kudos_map

    def may_require_key(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self.network != 'localhost' and (kwargs['account'] is None or kwargs['private_key'] is None):
                raise ValueError(f'Since you are on the {self.network} network, you must provide and account and private_key')
            else:
                return f(self, *args, **kwargs)
        return wrapper

    def retry(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            for i in range(1, 4):
                try:
                    f(self, *args, **kwargs)
                except BadFunctionCallOutput as e:
                    logger.warning(f'A network error occurred when trying to mint the Kudos.')
                    logger.warning('Retrying...')
                    time.sleep(1)
                    continue
                except KudosTransfer.DoesNotExist as e:
                    logger.warning('Retrying...')
                    time.sleep(1)
                    continue
                break
            return f(self, *args, **kwargs)
        return wrapper

    @retry
    def remove_kudos_orphans_db(self):
        """Sync up existing kudos from the blockchain to the database.

        Then remove all "orphaned Kudos" from the database.
        """

        latest_id = self._contract.functions.totalSupply().call()
        # if start_id == latest_id:
        #     return False
        # for kudos_id in range(start_id, latest_id + 1):
        #     # Try to link up any kudos_token and kudos_transfer objects
        #     # kudos_transfer = KudosTransfer.objects.get(pk=kudos_id)
        #     self.sync_db(kudos_id=kudos_id)

        # Remove orphaned Kudos in the database
        orphans = Token.objects.filter(pk__gt=latest_id)
        for orphan in orphans:
            logger.info('Removing Kudos orphan with ID: {orphan.id}')
        orphans.delete()

    def sync_db_without_txid(self, kudos_id):
        """The regular sync_db method should be preferred over this.

        This method is only to be used if you are syncing kudos directly from the blockchain
        and don't know the txid.

        The problem with not having a txid that is there is no good way to related it back
        to the kudos_transfer object.  Which means we don't know who the original sender is.

        Args:
            kudos_id (int): Kudos id.
        """
        kudos = self.getKudosById(kudos_id, to_dict=True)
        kudos['owner_address'] = self._contract.functions.ownerOf(kudos_id).call()
        if Token.objects.filter(pk=kudos_id).exists():
            kudos_token = Token.objects.get(pk=kudos_id)
            kudos['txid'] = kudos_token.txid
            updated_kudos_token = Token(pk=kudos_id, **kudos)
            updated_kudos_token.save()
        else:
            kudos_token = Token(pk=kudos_id, **kudos)
            kudos_token.save()
        logger.info(f'Synced id #{kudos_token.id}, "{kudos_token.name}" kudos to the database.')

    # @retry
    def sync_db(self, kudos_id, txid):
        """Sync up the Kudos contract on the blockchain with the database.

        Args:
            kudos_id (int): Kudos Id
            txid (str): The transaction hash.

        Returns:
            TYPE: Description
        """

        # Handle the dummy Kudos
        if kudos_id == 0:
            return False

        # Grab the Kudos from the blockchain, augment with owner_address
        kudos = self.getKudosById(kudos_id, to_dict=True)
        kudos['owner_address'] = self._contract.functions.ownerOf(kudos_id).call()

        # # Update an existing Kudos in the database
        # if Token.objects.filter(pk=kudos_id).exists():
        #     if txid:
        #         kudos['txid'] = txid
        #     kudos_token = Token(pk=kudos_id, **kudos)
        #     kudos_token.save(update_fields=list(kudos.keys()))
        # # Add a new Kudos to the database.  Require txid so we can link to kudos_transfer table.
        # else:
        #     if not txid:
        #         raise ValueError('Must provide a txid when syncing a new Kudos.')
        kudos['txid'] = txid
        kudos_token = Token(pk=kudos_id, **kudos)
        kudos_token.save()
        # Find the object which matches the kudos that was just cloned
        try:
            kudos_transfer = KudosTransfer.objects.get(receive_txid=txid)
        except KudosTransfer.DoesNotExist:
            # Only warn for a Kudos that is cloned/transfered, not a Gen0 Kudos.
            if kudos_token.num_clones_allowed == 0:
                logger.warning(f'No KudosTransfer object found for Kudos ID {kudos_id}')
                # raise KudosTransferNotFound(kudos_id, 'No KudosTransfer object found')
                raise
        else:
            # Store the foreign key reference if the kudos_transfer object exists
            kudos_transfer.kudos_token = kudos_token
            kudos_transfer.save()

        logger.info(f'Synced id #{kudos_token.id}, "{kudos_token.name}" kudos to the database.')

    def _get_contract_address(self):
        """Get the Kudos contract address, depending on the network.

        Returns:
            str: Kudos contract address.
        """
        if self.network == 'mainnet':
            return to_checksum_address('')
        elif self.network == 'ropsten':
            return to_checksum_address('0xcd520707fc68d153283d518b29ada466f9091ea8')
        elif self.network == 'rinkeby':
            return to_checksum_address('0x63aa4e5f76e7f5dcc762743880b3048412b37215')
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

    # @retry
    @may_require_key
    def mint(self, *args, account=None, private_key=None, skip_sync=False):
        """Contract transaction method.

        Mint a new Gen0 Kudos on the blockchain.  Not to be confused with clone.
        A clone() operation is only valid for an already existing Gen0 Kudos.

        From Kudos.sol:

        Args:
            *args: From Kudos.sol:
            mint(
                uint256 _priceFinney,
                uint256 _numClonesAllowed,
                string _tokenURI,
                )
            account (str, optional): Public account address.  Not needed for localhost testing.
            private_key (str, optional): Private key for account.  Not needed for localhost testing.

        Returns:
            TYPE: If a sync did occur, returns the kudos_id
        """
        account = self._resolve_account(account)

        if private_key:
            logger.debug('Private key found, creating raw transaction for Kudos mint...')
            nonce = self._w3.eth.getTransactionCount(account)
            gas_estimate = self._contract.functions.mint(*args).estimateGas({'nonce': nonce, 'from': account})
            txn = self._contract.functions.mint(*args).buildTransaction({'gas': gas_estimate, 'nonce': nonce, 'from': account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            logger.debug('No private key provided, using local signing...')
            tx_hash = self._contract.functions.mint(*args).transact({"from": account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
        logger.debug(f'Tx hash: {tx_hash.hex()}')

        kudos_id = self._contract.functions.totalSupply().call()
        logger.info(f'Minted id #{kudos_id} on the blockchain.')
        logger.info(f'Gas usage for id #{kudos_id}: {tx_receipt["gasUsed"]}')

        if not skip_sync:
            self.sync_db(kudos_id=kudos_id, txid=tx_hash.hex())

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
        self.sync_db(kudosid=kudos_id, txid=tx_hash.hex())

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
        self.sync_db(kudosid=kudos_id, txid=tx_hash.hex())

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
            returns (uint256 priceFinney, uint256 numClonesAllowed,
                     uint256 numClonesInWild, uint256 clonedFromId
                     )
        """
        kudos = self._contract.functions.getKudosById(args[0]).call()
        tokenURI = self._contract.functions.tokenURI(args[0]).call()
        ipfs_hash = tokenURI.split('/')[-1]

        metadata = self._ipfs.get_json(ipfs_hash)

        if to_dict:
            return self.get_kudos_map(kudos, metadata)
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

    # @retry_ipfs
    def create_tokenURI_url(self, **kwargs):
        """Create a tokenURI object, upload it to IPFS, and return the URL.

        Args:
            **kwargs:
                name (str):  Name of the kudos.
                image (str):  Image location of the kudos.  Should be a link to an image on the web.
                description (str):  Word description of the kudos.
                attributes (dict):  Dictionary containing attirbutes of the kudos.
                    tags (str): comma delimited tags.
                    number_of_clones_allowed (int): self explanatory.
                    rarity (int): integer from 0 to 100 (0 is most common).
                external_url (str):  External link to where the Kudos lives on the Gitcoin site.
                background_color (str):  Hex code.

        Returns:
            str: URL location on IPFS where the URI data is stored.
        """
        tokenURI = kwargs
        ipfs_hash = self._ipfs.add_json(tokenURI)
        ipfs_url = f'{settings.IPFS_HOST}:{settings.IPFS_API_PORT}/api/v0/cat/{ipfs_hash}'
        name = kwargs['name']
        logger.info(f'Posted metadata for "{name}" to IPFS.')
        logger.debug(f'ipfs_url for {kwargs["name"]}: {ipfs_url}')

        return ipfs_url
