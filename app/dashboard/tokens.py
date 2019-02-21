'''
    Copyright (C) 2019 Gitcoin Core

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


def get_tokens(network='mainnet'):
    from economy.models import Token
    return [token.to_dict for token in Token.objects.filter(network=network, approved=True).all()]


def addr_to_token(addr, network='mainnet'):
    for token in get_tokens(network=network):
        if(token['addr'].lower() == addr.lower()):
            return token
    return False


def token_by_name(name):
    for token in get_tokens():
        if token['name'].lower() == name.lower():
            return token
    return False
