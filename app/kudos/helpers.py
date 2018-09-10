# -*- coding: utf-8 -*-
'''
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

'''


def reconcile_kudos_preferred_wallet(profile):
    """Helper function to set the kudos_preferred_wallet if it doesn't already exist

    Args:
        profile (dashboard.modles.Profile): Instead of the profile model.

    Returns:  Kudos preferred wallet if found, else None.

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