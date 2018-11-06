# -*- coding: utf-8 -*-
"""Define helper functions.

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


def reconcile_kudos_preferred_wallet(profile):
    """DEPRECATED.
    Helper function to set the kudos_preferred_wallet if it doesn't already exist

    Args:
        profile (TYPE): Description

    Returns:
        str: Profile wallet address.

    """
    # If the preferred_kudos_wallet is not set, figure out how to set it.
    if not profile.preferred_kudos_wallet:
        # If the preferred_payout_address exists, use it for the preferred_kudos_Wallet
        if profile.preferred_payout_address and profile.preferred_payout_address != '0x0':
            # Check if the preferred_payout_addess exists as a kudos wallet address
            kudos_wallet = profile.wallets.filter(address=profile.preferred_payout_address).first()
            if kudos_wallet:
                # If yes, set that wallet to be the profile.preferred_kudos_wallet
                profile.preferred_kudos_wallet = kudos_wallet
                # profile.preferred_kudos_wallet = profile.wallets.filter(address=profile.preferred_payout_address)
            else:
                # Create the kudos_wallet and set it as the preferred_kudos_wallet in the profile
                new_kudos_wallet = Wallet(address=profile.preferred_payout_address)
                new_kudos_wallet.save()
                profile.preferred_kudos_wallet = new_kudos_wallet
        else:
            # Check if there are any kudos_wallets available.  If so, set the first one to preferred.
            kudos_wallet = profile.kudos_wallets.all()
            if kudos_wallet:
                profile.preferred_kudos_wallet = kudos_wallet.first()
            else:
                # Not enough information available to set the preferred_kudos_wallet
                # Use kudos indrect send.
                logger.warning('No kudos wallets or preferred_payout_address address found.  Use Kudos Indirect Send.')
                return None

        profile.save()

    return profile.preferred_kudos_wallet
