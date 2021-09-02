import secrets

import factory
from eth_utils import to_checksum_address
from grants.models.grant import Grant
from web3 import Web3

address = secrets.token_hex(20)


class GrantFactory(factory.django.DjangoModelFactory):
    """Create mock Grant for testing."""

    class Meta:
        model = Grant

    contract_address = Web3.toChecksumAddress(address)
