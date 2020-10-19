"""Define the burn kudos management command.

Copyright (C) 2020 Gitcoin Core

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
import time
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Profile
from kudos.models import Token, TokenRequest
from kudos.tasks import mint_token_request


class Command(BaseCommand):

    help = 'mints all kudos in the platform on xdai'

    def handle(self, *args, **options):
        # config
        counter = 0
        trs = TokenRequest.objects.filter(approved=True, network='mainnet')
        print(trs.count())
        for token in trs:
            already_xdaid = TokenRequest.objects.filter(network='xdai', name=token.name)
            if not already_xdaid:
                token.pk = None
                token.network = 'xdai'
                token.save()
                print(f'-/- {token.pk}')
                mint_token_request(token.pk)

        for token in Token.objects.filter(contract__network='mainnet'):
            if token.gen == 1 and not token.on_xdai:
                tr = TokenRequest.objects.create(
                    network='xdai',
                    name=token.name,
                    description=token.description,
                    priceFinney=token.priceFinney,
                    artist=token.artist,
                    platform=token.platform,
                    to_address=token.to_address,
                    numClonesAllowed=token.numClonesAllowed,
                    metadata=token.metadata,
                    tags=token.tags,
                    approved=True,
                    profile=Profile.objects.get(handle='gitcoinbot'),
                    processed=True,
                    )
                print(f'*/* {tr.pk}')
                mint_token_request(tr.pk)
