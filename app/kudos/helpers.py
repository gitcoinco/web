# -*- coding: utf-8 -*-
"""Define helper functions.

Copyright (C) 2021 Gitcoin Core

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
from django.shortcuts import get_object_or_404

from eth_utils import is_address, to_checksum_address

from .models import Contract, Token, Wallet

logger = logging.getLogger(__name__)


def get_token(token_id, network, address):
    """Helper to find the kudos.Token primary key, given the contract address and token_id fields.
    This function was created so that we can find the kudos token pk, only know the contract and
    token_id from the blockchain.  This is useful when linking to gitcoin from outside sites such
    as Open Sea.

    Args:
        token_id (int): The token_id field in the database (from blockchain)
        network (str): The ethereum network
        address (str): Contract address for this token (from blockchain)

    Returns:
        obj or None: Return Django object if found, else None.

    """
    try:
        contract = Contract.objects.get(
            address=address,
            network=network
        )
    except Exception as e:
        logger.warning(e)
        contract = Contract.objects.get(
            is_latest=True,
            network=network
        )

    return get_object_or_404(Token, contract=contract, token_id=token_id)


def re_send_kudos_transfer(kt, override_with_xdai_okay):
    from dashboard.utils import get_web3, has_tx_mined
    from gas.utils import recommend_min_gas_price_to_confirm_in_time
    from kudos.utils import kudos_abi
    from web3 import Web3
    from kudos.models import KudosTransfer
    from django.utils import timezone

    gas_clear_within_mins = 1
    gas_multiplier = 1.2

    if not kt.kudos_token_cloned_from.is_owned_by_gitcoin:
        print(f'{kt.id} => not owned by gitcoin')
        return

    network = kt.network
    if network == 'mainnet':
        if kt.kudos_token_cloned_from.on_xdai and override_with_xdai_okay:
            network = 'xdai'
            kt.network = 'xdai'
            kt.kudos_token_cloned_from = kt.kudos_token_cloned_from.on_xdai
            kt.save()
    w3 = get_web3(network)
    kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_MAINNET)
    if network == 'xdai':
        kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_XDAI)
    kudos_owner_address = Web3.toChecksumAddress(settings.KUDOS_OWNER_ACCOUNT)
    nonce = w3.eth.getTransactionCount(kudos_owner_address)

    token_id = kt.kudos_token_cloned_from.token_id
    address = kt.receive_address
    if not address:
        address = kt.recipient_profile.preferred_payout_address
    if not address:
        address = kt.recipient_profile.last_observed_payout_address
    price_finney = kt.kudos_token_cloned_from.price_finney

    try:

        contract = w3.eth.contract(Web3.toChecksumAddress(kudos_contract_address), abi=kudos_abi())
        gasPrice = int(gas_multiplier * float(recommend_min_gas_price_to_confirm_in_time(gas_clear_within_mins)) * 10**9)
        if network == 'xdai':
            gasPrice = 1 * 10**9
        tx = contract.functions.clone(Web3.toChecksumAddress(address), token_id, 1).buildTransaction({
            'nonce': nonce,
            'gas': 500000,
            'gasPrice': gasPrice,
            'value': int(price_finney / 1000.0 * 10**18),
        })

        signed = w3.eth.account.signTransaction(tx, settings.KUDOS_PRIVATE_KEY)
        txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
        nonce += 1
        print(f'sent tx nonce:{nonce} for kt:{kt.id} on {network}')
        kt.txid = txid
        kt.receive_txid = txid
        kt.tx_status = 'pending'
        kt.receive_tx_status = 'pending'
        kt.network = network
        kt.tx_time = timezone.now()
        kt.receive_tx_time = timezone.now()
        kt.save()
        return txid

    except Exception as e:
        print(e)
        error = "Could not redeem your kudos.  Please try again soon."
    return None
