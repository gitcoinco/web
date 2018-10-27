# -*- coding: utf-8 -*-
"""Define utility functions.

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
import re
import time
from functools import wraps

from django.conf import settings

import ipfsapi
from dashboard.utils import get_web3
from eth_utils import to_checksum_address
from git.utils import get_emails_master
from kudos.models import Contract, KudosTransfer, Token
from web3.exceptions import BadFunctionCallOutput

logger = logging.getLogger(__name__)


def humanize_name(name):
    """Turn snake_case into Snake Case.

    Returns:
        str: The humanized name.

    """
    return ' '.join([x.capitalize() for x in name.split('_')])


def computerize_name(name):
    """Turn Humanized Name into humanized_name.

    Returns:
        str: computerized_name
    """
    return name.lower().replace(' ', '_')


def get_rarity_score(num_clones_allowed):
    """Calculate rarity metrics based on the num_clones_allowed.

    Args:
        num_clones_allowed (int): Number of kudos clones allowed.

    Returns:
        str: Rarity description.

    Raises:
        ValueError: Raises an error if the number of clones allowed in less than one.
    """
    if not isinstance(num_clones_allowed, int):
        raise ValueError('num_clones_allowed must be an integer')

    if num_clones_allowed == 1:
        return 'One of a Kind'
    elif 2 <= num_clones_allowed <= 5:
        return 'Legendary'
    elif 6 <= num_clones_allowed <= 15:
        return 'Ultra'
    elif 16 <= num_clones_allowed <= 35:
        return 'Very Rare'
    elif 36 <= num_clones_allowed <= 100:
        return 'Rare'
    elif 101 <= num_clones_allowed <= 200:
        return 'Special'
    elif num_clones_allowed >= 201:
        return 'Common'
    else:
        raise ValueError('num_clones_allowed must be greater than or equal to 1')


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
        address (str): Eth address of the kudos contract
        network (str): The blockchain network (localhost, rinkeby, ropsten, mainnet)
    """

    def __init__(self, network='localhost', sockets=False):
        """Initialize the KudosContract.

        Args:
            network (str, optional): The blockchain network (localhost, rinkeby, ropsten, mainnet)
            sockets (bool, optional): Use web socket provider if set to True, otherwise use Http provider.

        """
        network = 'localhost' if network == 'custom network' else network
        self.network = network

        self._w3 = get_web3(self.network, sockets=sockets)

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
            metadata (dict): The metadata return from the tokenURI.

        Returns:
            dict: Kudos dictionary with key/values to be used to interact with the database.

        """
        mapping = dict(
            price_finney=kudos[0],
            num_clones_allowed=kudos[1],
            num_clones_in_wild=kudos[2],
            cloned_from_id=kudos[3],
        )

        attributes = metadata.pop('attributes')
        tags = []
        for attrib in attributes:
            if attrib['trait_type'] == 'rarity':
                mapping['rarity'] = attrib['value']
            elif attrib['trait_type'] == 'tag':
                tags.append(attrib['value'])
            elif attrib['trait_type'] == 'artist':
                mapping['artist'] = attrib['value']
            elif attrib['trait_type'] == 'platform':
                mapping['platform'] = attrib['value']

        mapping['tags'] = ', '.join(tags)

        # Add the rest of the fields
        kudos_map = {**mapping, **metadata}

        kudos_map['name'] = computerize_name(kudos_map['name'])
        kudos_map['image'] = re.sub(r'http.*?static\/', '', kudos_map['image'])

        return kudos_map

    def may_require_key(f):
        """Decorator to check if the operation needs a private key."""
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self.network != 'localhost' and (kwargs['account'] is None or kwargs['private_key'] is None):
                raise ValueError(f'Since you are on the {self.network} network, you must provide and account and private_key')
            else:
                return f(self, *args, **kwargs)
        return wrapper

    def log_args(f):
        """Decorator to log out the contract args."""
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            logger.debug(f'args: {args}')
            return f(self, *args, **kwargs)
        return wrapper

    def retry(f):
        """Decorator to retry a function if it failed."""
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
        """DEPRECATED.  This funciton must be updated to use.
        Sync up existing kudos from the blockchain to the database.

        Then remove all "orphaned Kudos" from the database.
        """

        latest_id = self._contract.functions.getLatestId().call()

        # Remove orphaned Kudos in the database
        orphans = Token.objects.filter(token_id__gt=latest_id)
        for orphan in orphans:
            logger.info('Removing Kudos orphan with ID: {orphan.id}')
        orphans.delete()

    def sync_db_without_txid(self, kudos_id):
        """DEPRECATED.
        The regular sync_db method should be preferred over this.

        This method is only to be used if you are syncing kudos directly from the blockchain
        and don't know the txid.

        The problem with not having a txid that is there is no good way to related it back
        to the kudos_transfer object.  Which means we don't know who the original sender is.

        Args:
            kudos_id (int): Kudos id.
        """
        kudos = self.getKudosById(kudos_id, to_dict=True)
        kudos['owner_address'] = self._contract.functions.ownerOf(kudos_id).call()
        kudos['contract_address'] = self._contract.address
        kudos['network'] = self.network
        if Token.objects.filter(token_id=kudos_id).exists():
            kudos_token = Token.objects.get(token_id=kudos_id)
            kudos['txid'] = kudos_token.txid
            updated_kudos_token = Token(token_id=kudos_id, **kudos)
            updated_kudos_token.save()
        else:
            kudos_token = Token(token_id=kudos_id, **kudos)
            kudos_token.save()
        logger.info(f'Synced id #{kudos_token.token_id}, "{kudos_token.name}" kudos to the database.')

    def sync_db(self, kudos_id, txid):
        """Sync up the Kudos contract on the blockchain with the database.

        Args:
            kudos_id (int): Kudos Id
            txid (str): The transaction hash.
        """

        # Handle the dummy Kudos
        if kudos_id == 0:
            return False

        # Grab the Kudos from the blockchain, augment with owner_address
        kudos = self.getKudosById(kudos_id, to_dict=True)
        kudos['owner_address'] = self._contract.functions.ownerOf(kudos_id).call()

        contract, created = Contract.objects.get_or_create(
            address=self._contract.address,
            network=self.network,
            defaults=dict(is_latest=True)
        )
        if created:
            old_contracts = Contract.objects.filter(network=self.network).exclude(id=contract.id)
            old_contracts.update(is_latest=False)

        # Update an existing Kudos in the database or create a new one
        kudos['txid'] = txid
        kudos_token, created = Token.objects.update_or_create(token_id=kudos_id, contract=contract, defaults=kudos)
        # Update the cloned_from_id kudos.  Namely the num_clones_in_wild field should be updated.
        if created:
            self.sync_db(kudos_id=kudos_token.cloned_from_id, txid=txid)
        # Find the object which matches the kudos that was just cloned
        try:
            kudos_transfer = KudosTransfer.objects.get(receive_txid=txid)
        except KudosTransfer.DoesNotExist:
            # Only warn for a Kudos that is cloned/transfered, not a Gen0 Kudos.
            if kudos_token.num_clones_allowed == 0:
                logger.warning(f'No KudosTransfer object found for Kudos ID {kudos_id}')
                # raise KudosTransferNotFound(kudos_id, 'No KudosTransfer object found')
                # raise
        else:
            # Store the foreign key reference if the kudos_transfer object exists
            kudos_transfer.kudos_token = kudos_token
            kudos_transfer.save()

        logger.info(f'Synced id #{kudos_token.token_id}, "{kudos_token.name}" kudos to the database.')

    def _get_contract_address(self):
        """Get the Kudos contract address, depending on the network.

        Returns:
            str: Kudos contract address.
        """
        if self.network == 'mainnet':
            return to_checksum_address(settings.KUDOS_CONTRACT_MAINNET)
        elif self.network == 'ropsten':
            return to_checksum_address(settings.KUDOS_CONTRACT_ROPSTEN)
        elif self.network == 'rinkeby':
            return to_checksum_address(settings.KUDOS_CONTRACT_RINKEBY)
        elif self.network == 'localhost' or self.network == 'custom network':
            # local testrpc
            return to_checksum_address(settings.KUDOS_CONTRACT_TESTRPC)
        else:
            raise ValueError('Unsupported network')

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

        Returns:
            str: The eth address of the account.

            TODO:  Should be consistent if we are returning a check summed address or not.

        Raises:
            RuntimeError: Return an error if it can't resolve the account.

        """
        if account:
            return to_checksum_address(account)

        try:
            return self._w3.eth.accounts[0]
        except IndexError:
            raise RuntimeError('Please specify an account to use for transacting with the Kudos Contract.')

    @log_args
    @may_require_key
    def mint(self, *args, account=None, private_key=None, skip_sync=False, gas_price_gwei=None):
        """Contract transaction method.

        Mint a new Gen0 Kudos on the blockchain.  Not to be confused with clone.
        A clone() operation is only valid for an already existing Gen0 Kudos.

        From Kudos.sol:

        Args:
            *args: From Kudos.sol:
            mint(
                address _to,
                uint256 _priceFinney,
                uint256 _numClonesAllowed,
                string _tokenURI,
                )
            account (str, optional): Public account address.  Not needed for localhost testing.
            private_key (str, optional): Private key for account.  Not needed for localhost testing.
            skip_sync (bool, optional):  If True, don't sync the database after the mint.

        Returns:
            int: If a sync did occur, returns the kudos_id
        """
        account = self._resolve_account(account)

        if private_key:
            logger.debug('Private key found, creating raw transaction for Kudos mint...')
            nonce = self._w3.eth.getTransactionCount(account)
            gas_estimate = self._contract.functions.mint(*args).estimateGas({'nonce': nonce, 'from': account})
            logger.debug(f'Gas estimate for raw tx: {gas_estimate}')
            if gas_price_gwei:
                gasPrice = self._w3.toWei(gas_price_gwei, 'gwei')
                txn = self._contract.functions.mint(*args).buildTransaction(
                    {'gasPrice': gasPrice, 'gas': gas_estimate, 'nonce': nonce, 'from': account}
                )
            else:
                txn = self._contract.functions.mint(*args).buildTransaction(
                    {'gas': gas_estimate, 'nonce': nonce, 'from': account}
                )
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            logger.debug('No private key provided, using local signing...')
            tx_hash = self._contract.functions.mint(*args).transact({"from": account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
        logger.debug(f'Tx hash: {tx_hash.hex()}')

        kudos_id = self._contract.functions.getLatestId().call()
        logger.info(f'Minted id #{kudos_id} on the blockchain.')
        logger.info(f'Gas usage for id #{kudos_id}: {tx_receipt["gasUsed"]}')

        if not skip_sync:
            self.sync_db(kudos_id=kudos_id, txid=tx_hash.hex())

        return kudos_id

    @may_require_key
    def clone(self, *args, account=None, private_key=None, skip_sync=False):
        """Contract transaction method.

        Args:
            *args: From Kudos.sol
            clone(
                 address _to,
                 uint256 _tokenId,
                 uint256 numClonesRequested
                 )
            account (str, optional): Public account address.  Not needed for localhost testing.
            private_key (str, optional): Private key for account.  Not needed for localhost testing.
            skip_sync (bool, optional):  If True, don't sync the database after the mint.

        Returns:
            int: The kudos_id
        """
        account = self._resolve_account(account)
        price_finney = self.getKudosById(args[1], to_dict=True)['price_finney']
        price_wei = self._w3.toWei(price_finney, 'finney')

        if private_key:
            logger.debug('Private key found, creating raw transaction...')
            nonce = self._w3.eth.getTransactionCount(account)
            gas_estimate = self._contract.functions.clone(*args).estimateGas({'nonce': nonce, 'from': account, 'value': price_wei})
            txn = self._contract.functions.clone(*args).buildTransaction({'gas': gas_estimate, 'nonce': nonce, 'from': account, 'value': price_wei})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            logger.debug('No private key provided, using local signing...')
            tx_hash = self._contract.functions.clone(*args).transact({"from": account, "value": price_wei})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
        logger.debug(f'Tx hash: {tx_hash.hex()}')

        kudos_id = self._contract.functions.getLatestId().call()
        logger.info(f'Cloned a new Kudos. id #{kudos_id} on the blockchain.')
        logger.info(f'Gas usage for id #{kudos_id}: {tx_receipt["gasUsed"]}')

        if not skip_sync:
            self.sync_db(kudos_id=kudos_id, txid=tx_hash.hex())

        return kudos_id

    @may_require_key
    def burn(self, *args, account=None, private_key=None, skip_sync=False):
        """Contract transaction method.

        Args:
            *args: From Kudos.sol
            burn(
                 address _owner,
                 uint256 _tokenId,
                 )
            account (str, optional): Public account address.  Not needed for localhost testing.
            private_key (str, optional): Private key for account.  Not needed for localhost testing.
            skip_sync (bool, optional):  If True, don't sync the database after the mint.

        Returns:
            int: The kudos_id
        """
        account = self._resolve_account(account)
        kudos_id = args[1]

        if private_key:
            logger.debug('Private key found, creating raw transaction...')
            nonce = self._w3.eth.getTransactionCount(account)
            gas_estimate = self._contract.functions.burn(*args).estimateGas({'nonce': nonce, 'from': account})
            txn = self._contract.functions.burn(*args).buildTransaction({'gas': gas_estimate, 'nonce': nonce, 'from': account})
            signed_txn = self._w3.eth.account.signTransaction(txn, private_key=private_key)
            tx_hash = self._w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        else:
            logger.debug('No private key provided, using local signing...')
            tx_hash = self._contract.functions.burn(*args).transact({"from": account})

        tx_receipt = self._w3.eth.waitForTransactionReceipt(tx_hash)
        logger.debug(f'Tx hash: {tx_hash.hex()}')

        logger.info(f'Burned Kudos with id #{kudos_id} on the blockchain.')
        logger.info(f'Gas usage to burn id #{kudos_id}: {tx_receipt["gasUsed"]}')

        if not skip_sync:
            self.sync_db(kudos_id=kudos_id, txid=tx_hash.hex())

        return kudos_id

    def getKudosById(self, *args, to_dict=False):
        """Contract call method.

        Args:
            *args: From Kudos.sol: getKudosById(uint256 tokenId)
            to_dict (bool, optional): Return a dictionary mapping instead of an array.

        Returns:
            list or dict: From Kudos.sol returns (uint256 priceFinney, uint256 numClonesAllowed,
                uint256 numClonesInWild, uint256 clonedFromId)
        """
        kudos = self._contract.functions.getKudosById(args[0]).call()
        tokenURI = self._contract.functions.tokenURI(args[0]).call()
        ipfs_hash = tokenURI.split('/')[-1]
        metadata = self._ipfs.get_json(ipfs_hash)

        if to_dict:
            return self.get_kudos_map(kudos, metadata)
        return kudos

    def getLatestId(self):
        """Contract call method.

        From Kudos.sol:
        getLatestId() view public returns (uint256 tokenId)

        Returns:
            int: The latest token id.

        """
        return self._contract.functions.getLatestId().call()

    def gen0_exists_db(self, kudos_name):
        """Helper method.

        Args:
            kudos_name (TYPE): Description

        Returns:
            bool: Whether or not the token name exists.

        """
        return Token.objects.filter(name__iexact=kudos_name).exists()

    def create_token_uri_url(self, **kwargs):
        """Create a tokenURI object, upload it to IPFS, and return the URL.

        Keyword Args:
            name (str):  Name of the kudos.
            image (str):  Image location of the kudos.  Should be a link to an image on the web.
            description (str):  Word description of the kudos.
            attributes (dict):  Dictionary containing attributes of the kudos.
                tags (str): comma delimited tags.
                number_of_clones_allowed (int): self explanatory.
                rarity (int): integer from 0 to 100 (0 is most common).
            external_url (str):  External link to where the Kudos lives on the Gitcoin site.
            background_color (str):  Hex code.

        Returns:
            str: URL location on IPFS where the URI data is stored.

        """
        ipfs_hash = self._ipfs.add_json(kwargs)
        return f'{settings.IPFS_API_SCHEME}://{settings.IPFS_HOST}:{settings.IPFS_API_PORT}/api/v0/cat/{ipfs_hash}'


def get_to_emails(params):
    """Get a list of email address to send the alert to, in this priority:

    1. get_emails_master() pulls email addresses from the user's public Github account.
    2. If an email address is included in the Tips/Kudos form, append that to the email list.


    Args:
        params (dict): A dictionary parsed form the POST request.  Typically this is a POST
            request coming in from a Tips/Kudos send.

    Returns:
        list: An array of email addresses to send the email to.

    """
    to_emails = []

    to_username = params['username'].lstrip('@')
    to_emails = get_emails_master(to_username)

    if params.get('email'):
        to_emails.append(params['email'])

    return list(set(to_emails))
