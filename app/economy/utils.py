'''
    Copyright (C) 2017 Gitcoin Core 

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
from economy.models import ConversionRate

# All Units in native currency


class TransactionException(Exception):
    pass


def convert_amount(from_amount, from_currency, to_currency):
    latest_conversion_rate = ConversionRate.objects.filter(
        from_currency=from_currency,
        to_currency=to_currency
        ).order_by('-timestamp').first()
    return (float(latest_conversion_rate.to_amount) / float(latest_conversion_rate.from_amount)) * float(from_amount)


def etherscan_link(txid):
    return 'https://etherscan.io/tx/' + txid
