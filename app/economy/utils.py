# -*- coding: utf-8 -*-
"""Define utilities and generic logic for the economy application.

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
from cacheops import cached_as
from economy.models import ConversionRate


# All Units in native currency
class TransactionException(Exception):
    """Handle general transaction exceptions."""

    pass


class ConversionRateNotFoundError(Exception):
    """Thrown if ConversionRate not found."""

    pass


def convert_amount(from_amount, from_currency, to_currency, timestamp=None):
    """Convert the provided amount to another current.

    Args:
        from_amount (float): The amount to be converted.
        from_currency (str): The currency identifier to convert from.
        to_currency (str): The currency identifier to convert to.
        timestamp (datetime): First available conversion rate after timestamp. Latest if None.

    Returns:
        float: The amount in to_currency.

    """

    # hack to handle WETH
    if from_currency == 'WETH':
        from_currency = 'ETH'
    if to_currency == 'WETH':
        to_currency = 'ETH'
    
    if timestamp:
        conversion_rate = ConversionRate.objects.filter(
            from_currency=from_currency,
            to_currency=to_currency,
            timestamp__gte=timestamp
        ).order_by('-timestamp').last()
    else:
        conversion_rate = ConversionRate.objects.filter(
            from_currency=from_currency,
            to_currency=to_currency,
        ).order_by('-timestamp').first()

    if not conversion_rate:
        raise ConversionRateNotFoundError(f"ConversionRate {from_currency}/{to_currency} @ {timestamp} not found")

    return (float(conversion_rate.to_amount) / float(conversion_rate.from_amount)) * float(from_amount)


def convert_token_to_usdt(from_token, timestamp=None):
    """Convert the token to USDT.

    Args:
        from_token (str): The token identifier.

    Returns:
        float: The current rate of the provided token to USDT.

    """
    try:
        return convert_amount(1, from_token, "USDT", timestamp)
    except ConversionRateNotFoundError:
        in_eth = convert_amount(1, from_token, "ETH", timestamp)
        return convert_amount(in_eth, 'ETH', "USDT", timestamp)


def etherscan_link(txid):
    """Build the Etherscan URL.

    Args:
        txid (str): The transaction ID.

    Returns:
        str: The Etherscan TX URL.

    """
    return f'https://etherscan.io/tx/{txid}'
