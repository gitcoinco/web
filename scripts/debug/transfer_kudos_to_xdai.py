name = 'future_city'

import logging
import time
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Profile
from kudos.models import Token, TokenRequest
from kudos.tasks import mint_token_request

token = Token.objects.filter(contract__network='mainnet', name=name, num_clones_allowed__gt=1).first()
print(token)

tr = TokenRequest.objects.create(
    network='xdai',
    name=token.name,
    description=token.description,
    priceFinney=token.price_finney,
    artist=token.artist,
    platform=token.platform,
    to_address=token.owner_address,
    numClonesAllowed=token.num_clones_allowed,
    metadata=token.metadata,
    tags=token.tags.split(','),
    artwork_url=token.image,
    approved=True,
    profile=Profile.objects.get(handle='gitcoinbot'),
    processed=True,
    )
print(f'*/* {tr.pk}')
mint_token_request(tr.pk, send_notif_email=False)
